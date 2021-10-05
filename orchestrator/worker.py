import workloads
try:
    import usocket as socket
except:
    import socket
try:
    import ujson as json
except:
    import json
try:
    import utime as time
except:
    import time
def shutdown():
    return workloads.fwrite({'path': "/proc/sysrq-trigger", 'data': "o"})
def reboot():
    return workloads.fwrite({'path': "/proc/sysrq-trigger", 'data': "b"})

s = socket.socket()
ai = socket.getaddrinfo("192.168.1.2", 63302)
addr = ai[0][-1]
s.connect(addr)
# Send a few garbage bytes as our ID, forcing orchestrator
# to use our IP as an ID
s.write(b"pl\n")
# Receive JSON-packed command from orchestrator
cmd_json = s.readline()
print("DEBUG: Orchestrator offers: " + str(cmd_json))
try:
    cmd = json.loads(cmd_json)
except ValueError:
    print("ERR: Orchestrator sent malformed JSON!")
    s.close()
    reboot()
# Try to execute the requested function
begin_exec_time = time.ticks_ms()
try:
    result = workloads.FUNCTIONS[cmd['f_id']](cmd['f_args'])
except KeyError:
    print("ERR: Bad function ID or malformed array")
    s.close()
    reboot()
end_exec_time = time.ticks_ms()
# Construct the reply to the orchestrator
reply = {
    'f_id': cmd['f_id'],
    'i_id': cmd['i_id'],
    'result': result,
    'exec_time': time.ticks_diff(end_exec_time, begin_exec_time)
}
# Send the result back to the orchestrator
s.write(json.dumps(reply) + "\n")

# Receive the followup command (usually reboot or shutdown)
cmd_json = s.readline()
print("DEBUG: Orchestrator offers follow-up: " + str(cmd_json))
try:
    cmd = json.loads(cmd_json)
except ValueError:
    print("ERR: Orchestrator sent malformed JSON follow-up!")
    s.close()
    reboot()

# Close the socket
s.close()

# Run the final followup command
workloads.FUNCTIONS[cmd['f_id']](cmd['f_args'])

# Then we'll probably be forcibly rebooted/shutdown

# Sleep to prevent race condition between poweroff and reboot
time.sleep(1)

# If we make it here, things are getting weird
print("WARN: Follow-up command allowed execution to continue. Rebooting...")

# Immediate Shutdown
reboot()
