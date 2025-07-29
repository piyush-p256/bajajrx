# main/utils.py
import time
import requests
from functools import wraps

def retry_with_backoff(max_retries=5, backoff_factor=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            delay = 1
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except requests.exceptions.RequestException as e:
                    if e.response is not None and e.response.status_code == 429:
                        print(f"[!] Rate limited. Retrying in {delay}s...")
                        time.sleep(delay)
                        delay *= backoff_factor
                        retries += 1
                    else:
                        raise e
            raise Exception(f"Failed after {max_retries} retries.")
        return wrapper
    return decorator
