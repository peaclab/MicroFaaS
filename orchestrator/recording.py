import csv
from json import loads, JSONDecodeError
import logging as log
import os
from threading import Lock

class ThreadsafeCSVWriter:
    def __init__(self, metric_path="microfaas-log.csv", result_path="microfaas-results.csv") -> None:
        self._file_lock = Lock()
        self._metric_file_handle = open(metric_path, "a+t")
        self._result_file_handle = open(result_path, "a+t")
        self._metric_writer = csv.DictWriter(
            self._metric_file_handle,
            fieldnames=[
                "invocation_id",
                "worker",
                "function_id",
                "exec_time",
                "rtt",
                "timestamp"
            ],
        )
        self._result_writer = csv.DictWriter(
            self._result_file_handle,
            fieldnames=[
                "invocation_id",
                "result",
            ],
        )

        with self._file_lock:
            self._metric_writer.writeheader()
            self._metric_file_handle.flush()
            os.fsync(self._metric_file_handle)

            self._result_writer.writeheader()
            self._result_file_handle.flush()
            os.fsync(self._result_file_handle)

    def __del__(self):
        with self._file_lock:
            self._metric_file_handle.flush()
            os.fsync(self._metric_file_handle)
            self._metric_file_handle.close()

            self._result_file_handle.flush()
            os.fsync(self._result_file_handle)
            self._result_file_handle.close()

    def save_raw_result(self, worker_id, data_json, rtt, timestamp):
        """
        Process and save a raw JSON string recv'd from a worker to CSV
        """

        # data_json should look like {i_id, f_id, result, exec_time}
        # where exec_time is in milliseconds
        try:
            data = loads(data_json)
        except JSONDecodeError as e:
            log.error("Cannot save malformed JSON from worker %s: %s", worker_id, e)
            return False

        # Convert relative timestamps to absolutes, and milliseconds to fractional seconds
        try:
            metric_row = {
                "invocation_id": data["i_id"],
                "worker": worker_id,
                "function_id": data["f_id"],
                "exec_time": int(data["exec_time"]),
                "rtt": int(rtt),
                "timestamp": timestamp
            }

            result_row = {
                "invocation_id": data["i_id"],
                "result": data['result']
            }
        except KeyError as e:
            log.error("Bad schema: %s", e)
            return False
        except ValueError as e:
            log.error("Bad cast: %s", e)
            return False

        with self._file_lock:
            self._metric_writer.writerow(metric_row)
            self._metric_file_handle.flush()
            os.fsync(self._metric_file_handle)

            self._result_writer.writerow(result_row)
            self._result_file_handle.flush()
            os.fsync(self._result_file_handle)

        return metric_row['invocation_id']