import time
from collections import defaultdict

attempts = defaultdict(list)

def is_rate_limited(ip):
    now = time.time()
    attempts[ip] = [t for t in attempts[ip] if now - t < 900]
    if len(attempts[ip]) >= 5:
        return True
    return False

def record_attempt(ip):
    attempts[ip].append(time.time())
