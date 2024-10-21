import os
import time

group_cnt = 26

for i in range(1, group_cnt + 1):
    os.system(f"python check-gitlab.py {i} 5")
    time.sleep(1)
