import psutil
import time

busy_pids = set()

while True:
    busy_now = set()
    no_longer_busy = set()
    for pid in psutil.pids():
        p = psutil.Process(pid)
        if p.name() == 'apache2' and p.cpu_times().user > 30.0 and p.cpu_percent(interval=1.0) > 90.0:
            busy_now.add(pid)
    for pid in busy_pids:
        if not pid in busy_now:
            no_longer_busy.add(pid)
    for pid in no_longer_busy:
        busy_pids.discard(pid)
    for pid in busy_now:
        if pid in busy_pids:
            p = psutil.Process(pid)
            p.kill()
            busy_pids.discard(pid)
        else:
            busy_pids.add(pid)
    time.sleep(30)
