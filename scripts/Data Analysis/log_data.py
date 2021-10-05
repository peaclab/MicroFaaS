import os
from posixpath import join
import time
import datetime
import string

# CONSTANTS
NUM_JOBS = 17000
DIRECTORY = './'
START_TIME = 0
END_TIME = 0
END_SEC = 0
START_SEC = 0
FMT = '%H:%M:%S'
TOTAL_RUN_TIME = 0
FUNPERMIN = 0
CPU_AVG_1MIN = 0.0
CPU_AVG_10MIN = 0.0
CPU_AVG_15MIN = 0.0
IDLE_MEM = 0
MEM_AVG = 0.0
WATT_HOUR = 0.0
JOULES_PER_FUNC = 0.0
WATT = 0.0

# Loop through to find START_TIME and END_TIME in orchestrator
for filename in os.listdir(DIRECTORY):
    # Defensive programming check to make sure file is not corrupted
    file = os.path.join(DIRECTORY, filename)
    if os.path.isfile(file):
        # Parse orchestrator log
        if 'orch' in filename:
            f = open(file)
            lines = f.readlines()
            # Flag to check if last line was powering on a VM
            powerFlag = False
            # Counter to skip excess log data from previous log
            skipCount = 0
            # Find the first transmitted work after powering on VM
            for line in lines:
                # Skip the first 10 lines of excess log data
                if skipCount <= 10:
                    skipCount += 1
                    continue
    
                if 'power up' in line:
                    powerFlag = True
                elif 'power up' not in line and powerFlag == True:
                    # Index the time stamp
#                    print("got start line", line)
                    START_TIME = line.split(' ')[2]
                    break
                
            # Find the first to last transmitted work
            for line in lines[-1:0:-1]:
                if 'Transmitted work' in line:
                    # Index the time stamp
                    END_TIME = line.split(' ')[2]
                    break

            # Calculate time delta between first and last function calls
            TOTAL_RUN_TIME = (datetime.datetime.strptime(str(END_TIME), FMT) - datetime.datetime.strptime(str(START_TIME), FMT)).seconds
            print('\nFirst Transmitted Work: ' + str(START_TIME))
            print('Last Transmitted Work: ' + str(END_TIME))
            print('Total runtime in seconds: '+ str(TOTAL_RUN_TIME) + 's')
            print('Functions per minute: ' + str(( NUM_JOBS * 60/float(TOTAL_RUN_TIME))))


            # Close file
            f.close()

            # Convert START_TIME and END_TIME to seconds fo`r relevant log range comparison
            startTime = time.strptime(str(START_TIME), FMT)
            START_SEC = datetime.timedelta(hours=startTime.tm_hour,minutes=startTime.tm_min,seconds=startTime.tm_sec).total_seconds()
            endTime = time.strptime(END_TIME, FMT)
            END_SEC = datetime.timedelta(hours=endTime.tm_hour,minutes=endTime.tm_min,seconds=endTime.tm_sec).total_seconds()

# Parse through all other files in directory
for filename in os.listdir(DIRECTORY):
    # Defensive programming check to make sure file is not corrupted
    file = os.path.join(DIRECTORY, filename)
    if os.path.isfile(file):
        # Reading CPU log for CPU utilization
        if 'cpu' in filename:
            f = open(file)
            lines = f.readlines()
            count = 0
            for line in lines:
                # Convert current time to seconds for relevant log range comparison
                currTime = time.strptime(line.split(' ')[1], FMT)
                currSeconds = datetime.timedelta(hours=currTime.tm_hour,minutes=currTime.tm_min,seconds=currTime.tm_sec).total_seconds()

                # When the current time stamp is between the start and end seconds, increment the running average for cpu utilization and the counter variable
                if currSeconds <= END_SEC and currSeconds >= START_SEC:
                    count += 1
                    tmpList = line.split('load average:')[1].split(',')
                    CPU_AVG_1MIN += float(tmpList[0])
                    CPU_AVG_10MIN += float(tmpList[1])
                    CPU_AVG_15MIN += float(tmpList[2])
                elif currSeconds > END_SEC:
                    break
                else:
                    continue
                    
            # Average the running cpu utilization by the number of instances uptime was performed
            CPU_AVG_1MIN /= count
            CPU_AVG_10MIN /= count
            CPU_AVG_15MIN /= count
            print('\nAverage CPU Utilization from idle (1min, 10min, 15min): ' + str(CPU_AVG_1MIN) + ', ' + str(CPU_AVG_10MIN) + ', ' + str(CPU_AVG_15MIN))

            
            # Close file
            f.close()

        # Reading MEM log for MEM utilization
        elif 'mem' in filename:
            f = open(file)
            lines = f.readlines()
            
            # Flag to check for IDLE MEM used
            firstMemFlag = True
            count = 0
            
            for line in lines:
                # Take the first instance of used mem as idle mem utilization
                if firstMemFlag == True and 'Mem:' in line:
                    firstMemFlag = False
                    IDLE_MEM = line.split()[2]
                # Get the timestamp and convert to seconds for relevent log comparison
                elif 'total' not in line and 'Mem:' not in line and 'Swap:' not in line:
                    currTime = time.strptime(line.split()[0], FMT)
                    currSeconds = datetime.timedelta(hours=currTime.tm_hour,minutes=currTime.tm_min,seconds=currTime.tm_sec).total_seconds()
                # For all lines that include mem readings, are not the first one, and are between the start and end time, add used mem into a running average
                elif currSeconds < END_SEC and currSeconds > START_SEC and firstMemFlag == False and 'Mem:' in line:
                    # Add mem usage by VM while removing idle mem usage
                    MEM_AVG += float(line.split()[2]) - float(IDLE_MEM)
                    count += 1
                # If the current time is past experiment, stop reading the log
                elif currSeconds > END_SEC:
                    break
            
            # Calculate average MEM utilization
            MEM_AVG /= count
            print('\nAverage MEM utilization from idle: ' + str(MEM_AVG))

            # Close file
            f.close()
        
        # Reading energy log for energy consumption by VMs
        elif 'energy' in filename:
            f = open(file)
            lines = f.readlines()
            count=0

            for line in lines:
                # Isolate the time stamp. These timestamps start from 0, so they are compared to TOTAL_RUN_TIME
                currTime = float(line.split()[0][1:])
                # Once the current time excedes the total run time, the experiment has been completed and we can index the watt-hour value
                if currTime >= TOTAL_RUN_TIME:
                    WATT_HOUR = int(line.split(',')[6]) /10
                    break
                elif currTime >= 1:
                    count +=1
                    WATT +=  int(line.split(',')[5]) /10
            # 1mW-hour = 3.6 Joules
            # Divide Joules by number of jobs for Joules per function
            JOULES_PER_FUNC = WATT_HOUR * 1000 * 3.6 / NUM_JOBS
            print("\nWatt-Hr: " + str(WATT_HOUR ))
            print("Joules per Function: " + str(JOULES_PER_FUNC))
            print("Average Watts: "+ str(WATT/count))


        # Reading results log for function analytics        
        # elif 'results' in filename:
        #     print('PARSING ' + filename)

