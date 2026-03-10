
import schedule
import time
import datetime

def job():
    print(f"Job ran at {datetime.datetime.now()}")

# Set run time to 2 seconds from now
now = datetime.datetime.now()
run_time = (now + datetime.timedelta(seconds=2)).strftime("%H:%M:%S")
print(f"Scheduling job for {run_time}")

schedule.every().day.at(run_time).do(job)

# Simulation loop
start_time = time.time()
while time.time() - start_time < 5:
    schedule.run_pending()
    time.sleep(0.1)

print("Finished simulation")
