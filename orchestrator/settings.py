# NC Server IP
NC_IP = '192.168.1.201'
NC_PORT = 1152

# Socket timeout
SOCK_TIMEOUT = 120

# TCP Server Setup
# Host "" means bind to all interfaces
# Port 0 means to select an arbitrary unused port
HOST, PORT = "", 63302

# How many total functions to run across all workers
FUNC_EXEC_COUNT = 17000

# How often to populate queues (seconds)
LOAD_GEN_PERIOD = 1

# Minimum severity of displayed log messages (DEBUG, INFO, WARNING, ERROR, or CRITICAL)
LOG_LEVEL = "INFO"

# How long (in seconds) to wait after each worker status check to begin another
MONITOR_PERIOD = 0.2

# How many seconds to "hold down the power button" when powering-up BBBWorkers 
BTN_PRESS_DELAY = 0.5

# How long (in seconds) to wait for a worker to make a post-boot connection before retrying
LAST_CONNECTION_TIMEOUT = 10

# Job timeout
JOB_TIMEOUT = 120

# How long to wait for a worker to boot
POWER_UP_TIMEOUT = 60

# How long to wait for a worker in an "unknown" state to connect before taking corrective action
UNKNOWN_TIMEOUT = 30

# How long (in seconds) to wait after script start before issuing power up/down commands
# Useful if you're starting an experiment with pre-powered-up workers
POWER_UP_HOLDOFF_BBB = 10
POWER_UP_HOLDOFF_VM = 0
POWER_DOWN_HOLDOFF_BBB = 10
POWER_DOWN_HOLDOFF_VM = 10

# Worker Setup
# WORKERS maps worker IDs to GPIO lines or MAC-addrs 
# We assume the ID# also maps to the last octet of the worker's IP
# e.g., if the orchestrator is 192.168.1.2, and workers are 192.168.1.3-12, IDs should be range(3, 13)
# Format of AVAILABLE WORKERS: { "worker_id": ("WorkerClassName", "pin")}
AVAILABLE_WORKERS = {
    "3": ("BBBWorker", "P9_12"),
    "4": ("BBBWorker", "P9_15"),
    "5": ("BBBWorker", "P9_23"),
    "6": ("BBBWorker", "P9_25"),
    "7": ("BBBWorker", "P9_27"),
    "8": ("BBBWorker", "P8_8"),
    "9": ("BBBWorker", "P8_10"),
    "10": ("BBBWorker", "P8_11"),
    "11": ("BBBWorker", "P8_14"),
    "12": ("BBBWorker", "P9_26"),
    "103": ("VMWorker", ":03"),
    "104": ("VMWorker", ":04"),
    "105": ("VMWorker", ":05"),
    "106": ("VMWorker", ":06"),
}
