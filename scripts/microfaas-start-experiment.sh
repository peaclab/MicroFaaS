#!/bin/bash

# exit when any command fails
set -e
trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM ERR

PWR_HOST="yanni@silber.n-x.win"
#PWR_HOST="allenzou@192.168.1.200"
PWR_TTY=/dev/ttyUSB0
ORCH_HOST="debian@192.168.1.2"
VM_HOST="allenzou@192.168.1.201"
TS=$(date --date='TZ="America/New_York" now' +%Y-%m-%d.%I%M%S%p)
ID_FLAG="${@:2}"

while [[ "$1" =~ ^- && ! "$1" == "--" ]]; do case $1 in
    -m | --vm)
        shift; VM_MODE=1
        ;;
    -b | --bb)
        shift; VM_MODE=0
        ;;
    -h | --help)
        echo "microfaas-start-experiment.sh options:"
        echo "   -m | --vm : run the experiment using VM cluster"
        echo "   -b | --bb : run the experiment using BeagleBone cluster"
        echo "   Always specify number of workers by adding it at the END of the bash command"
        exit
        ;;
esac; shift; done

if [ $VM_MODE == 1 ]; then
	PRE=microfaas-vm
	UNIT=microfaas-vm.service
else
	PRE=microfaas-bbb
	UNIT=microfaas.service
fi
DNAME=$PRE-logs.$TS 
mkdir $DNAME

# Start power logging
ssh $PWR_HOST "grabserial -td $PWR_TTY --command='\#R,W,0;'" > $DNAME/$PRE.energy.$TS.log &
PWR_PID=$!

# Start daemon logging
ssh $ORCH_HOST "journalctl -u $UNIT -f" > $DNAME/$PRE.orch.$TS.log &
DAEMON_PID=$!

# Start CPU and MEM logging
ssh $VM_HOST "while true; do uptime; sleep 5; done" >> $DNAME/$PRE.cpu.$TS.log &
CPU_PID=$!
ssh $VM_HOST "while true; date +\"%T\";do free -m; sleep 5; done" >>$DNAME/$PRE.mem.$TS.log &
MEM_PID=$!
# Configure number of workers
ssh $ORCH_HOST "echo \"ARG1=\"$ID_FLAG\"\" > /etc/.argconf"

# Start orchestrator
ssh $ORCH_HOST "sudo -n systemctl restart $UNIT"

# Log results
sleep 20
if [ $VM_MODE == 1 ]; then
        ssh $ORCH_HOST "tail -qF ~/MicroFaaS/\`ls -Art ~/MicroFaaS | grep vm.results| tail -n 1\`" >> $DNAME/$PRE.results.$TS.log &
else
        ssh $ORCH_HOST "tail -qF ~/MicroFaaS/\`ls -Art ~/MicroFaaS | grep bb.results | tail -n 1\`" >> $DNAME/$PRE.results.$TS.log &
fi
LOG_PID=$!

echo "To end the experiment, run: kill $PWR_PID $DAEMON_PID $LOG_PID"

tail -f $DNAME/$PRE.orch.$TS.log
