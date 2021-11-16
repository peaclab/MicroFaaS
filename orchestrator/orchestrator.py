#!/usr/bin/env python3
import argparse
import json
import logging as log
import queue
import random
import socket
import socketserver
import string
import threading
import time
from datetime import datetime, timedelta
from json.decoder import JSONDecodeError

from numpy import random as nprand

import settings as s
from recording import ThreadsafeCSVWriter
from workers import BBBWorker, VMWorker
from commands import COMMANDS

# Log Level
log.basicConfig(level=s.LOG_LEVEL)
log.getLogger().setLevel(s.LOG_LEVEL)

# Check command line argument for VM flag
parser = argparse.ArgumentParser()
parser.add_argument('--vm', action='store_true', help="Only use VMWorkers")
parser.add_argument('--bbb', action='store_true', help="Only use BBBWorkers")
parser.add_argument('--ids', action="store", help="Only use workers with specified IDs in comma-separated list (may be further constrained by --vm or --bbb)")
ARGS = parser.parse_args()

# Generate worker set
def worker_from_tuple(id, worker_tuple):
    if worker_tuple[0] == "BBBWorker":
        return BBBWorker(int(id), worker_tuple[1])
    elif worker_tuple[0] == "VMWorker":
        return VMWorker(int(id), worker_tuple[1])
    else:
        raise RuntimeError("Bad worker specification: {} {}".format(id, worker_tuple))

WORKERS = {}
for id, worker_tuple in s.AVAILABLE_WORKERS.items():
    try:
        WORKERS[id] = worker_from_tuple(id, worker_tuple)
    except RuntimeError as ex:
        log.error("Failed to create worker {}: {}", id, ex)

POSTFIX = ""
if ARGS.vm and ARGS.bbb:
    raise argparse.ArgumentError("Cannot combine options --vm and --bbb")
elif ARGS.vm:
    log.info("User requested we use VMWorkers only")
    WORKERS = {k:v for k,v in WORKERS.items() if isinstance(v, VMWorker)}
    POSTFIX = "-vm"
elif ARGS.bbb:
    log.info("User requested we use BBBWorkers only")
    WORKERS = {k:v for k,v in WORKERS.items() if isinstance(v, BBBWorker)}
    POSTFIX = "-bbb"

if ARGS.ids is not None:
    requested_ids = [int(x.strip()) for x in ARGS.ids.split(",")]
    WORKERS = {k:v for k,v in WORKERS.items() if v.id in requested_ids}

log.info("Activating the following workers: %s", list(WORKERS.values()))
for w in WORKERS.values():
    w.activate()

START_TIME = datetime.now()

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        # Set the timeout for blocking socket operations
        self.request.settimeout(s.SOCK_TIMEOUT)

        # First check if worker identified itself
        log.debug("Incoming request from %s", self.client_address[0])
        try:
            # If first few bytes can be casted to an int, assume it's an ID
            self.worker_id = int(self.request.recv(4).strip())
        except ValueError:
            # Otherwise try to identify the worker by its IP address
            try:
                self.worker_id = int(self.client_address[0].split(".")[-1])
            except ValueError:
                log.error(
                    "Could not deduce worker ID for %s. Dropping request.",
                    self.client_address[0],
                )
                return
        except ConnectionResetError or ConnectionAbortedError:
            # Ignorable: occurs when worker powers off in the middle of a request
            log.debug("Connection reset during worker identification")
            return

        # Record this connection on the Worker object
        try:
            w = WORKERS[str(self.worker_id)]
        except KeyError:
            # Unknown or inactive worker connected, try to shutdown
            try:
                # See if worker is known-but-inactive
                worker_tuple = s.AVAILABLE_WORKERS[str(self.worker_id)]
                pwr_down_payload = worker_from_tuple(self.worker_id, worker_tuple).power_down_inactive()
                if pwr_down_payload is not None:
                    self.request.sendall(pwr_down_payload)
                log.warn("Inactive worker %s attempted to connect, told to power down", self.worker_id)
            except KeyError:
                # Connected worker is completely unknown, all we can do is ignore it 
                log.error("Worker with unknown ID %s attempted to connect", self.worker_id)
            return

        # Send the worker the next item on the queue
        ascii_encoded_json_job = w.handle_worker_request(1)
        send_time = time.monotonic() * 1000
        self.request.sendall(ascii_encoded_json_job)
        log.info("Transmitted work to %s", w)
        log.debug(ascii_encoded_json_job)

        # Now we wait for work to happen and results to come back
        # The socket timeout will limit how long we wait
        try:
            self.data = self.request.recv(12288).strip()
            recv_time = time.monotonic() * 1000
        except socket.timeout:
            log.error("Timed out waiting for worker %s to run %s", self.worker_id, ascii_encoded_json_job)
            return
        except ConnectionResetError or ConnectionAbortedError:
            # Occurs when worker powers off in the middle of a request. Kinda unusual mid-job
            log.warning("Connection reset while waiting for %s to run %s", w, ascii_encoded_json_job)
            return

        # Calculate Round Trip Time
        rtt = recv_time - send_time

        # Save results to CSV
        log.debug("Worker %s returned: %s", self.worker_id, self.data)
        writer_result = writer.save_raw_result(self.worker_id, self.data, rtt, time.strftime("%Y-%m-%d %H:%M:%S"))
        if not writer_result:
            log.error("Failed to process results from worker %s!", self.worker_id)
        else:
            log.info("Processed results of invocation %s from worker %s", writer_result, self.worker_id)

        # Handle the second worker request: usually says to either shutdown or reboot
        try:
            self.request.sendall(w.handle_worker_request(2))
        except TypeError:
            log.warning("Telling %s to reboot due to unhandled request", w)
            self.request.sendall(w.reboot_payload())
        log.debug("Finished handling %s", w)


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    def server_bind(self) -> None:
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)
        log.info("Server thread bound to %s", self.server_address)
        return


def load_generator(count):
    """
    Load generation thread. Run as daemon

    Every period, picks a random number of workers and puts a new job on their queue
    """
    log.info("Load generator started (limit: %d total invocations)", count)
    # Ensure jobs are run in a balanced way
    job_counts = dict({k:(count // len(COMMANDS)) for k, _ in COMMANDS.items()})
    while count > 0:
        for _, w in random.sample(WORKERS.items(), random.randint(1,len(WORKERS))):
            try:
                f_id = random.choice(list(COMMANDS.keys()))
            except IndexError:
                log.debug("COMMANDS is empty, continuing...")
                continue

            cmd = {
                # Invocation ID
                "i_id": "".join(
                    random.choices(string.ascii_letters + string.digits, k=6)
                ),
                # Function ID (one of COMMANDS.keys())
                "f_id": f_id,
                # Function arguments
                "f_args": random.choice(COMMANDS[f_id]),
            }
            w.enqueue_job((json.dumps(cmd) + "\n").encode(encoding="ascii"))
            #log.debug("Added job to worker %s's queue: %s", w.id, json.dumps(cmd))

            # Keep track of how many times we've run this job
            job_counts[f_id] -= 1
            if job_counts[f_id] <= 0:
                # If we've run it enough, remove it from the list of commands
                log.info("Enough invocations of %s have been queued up, so popping from COMMANDS", f_id)
                COMMANDS.pop(f_id, None)

            count -= 1
        time.sleep(s.LOAD_GEN_PERIOD)
    log.info("Load generator exiting (queuing complete)")

if __name__ == "__main__":

    # Set up CSV writer
    writer = ThreadsafeCSVWriter("microfaas{}.results.{}.csv".format(POSTFIX, datetime.now().strftime("%Y-%m-%d.%I%M%S%p"),))

    # Set up load generation thread
    load_gen_thread = threading.Thread(
        target=load_generator, daemon=False, args=(s.FUNC_EXEC_COUNT,)
    )
    load_gen_thread.start()

    # Set up server thread
    server = ThreadedTCPServer((s.HOST, s.PORT), ThreadedTCPRequestHandler)
    with server:
        ip, port = server.server_address

        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        server_thread = threading.Thread(target=server.serve_forever)
        # Run the server thread when the main thread terminates
        server_thread.daemon = False
        server_thread.start()
        #print("Server loop running in thread:", server_thread.name)

        # Run at least until we finish queuing up our workloads
        load_gen_thread.join()

        # Then check if it's been a while since our last request
        all_queues_not_empty = True
        while all_queues_not_empty:
            all_queues_not_empty = False
            for _, w in WORKERS.items():
                all_queues_not_empty = all_queues_not_empty or not w.job_queue_empty()
            time.sleep(2)

        server.shutdown()
