from redis import Redis
from rq import Queue
from mars_demo.mars import get_mars_photo

# Start the sever
#subprocess.Popen("bash /media/data/OneDrive/Documents/Graduate School/2020.1/601R - Big Data/redis/redis-5.0.7/src/redis-server", shell=True)

q = Queue(connection=Redis())

for i in range(10):
    q.enqueue(get_mars_photo, 990 + i) # enqueue the function

# Requeue failed jobs:
# rq requeue --queue myqueue -u redis://localhost:6379 --all
