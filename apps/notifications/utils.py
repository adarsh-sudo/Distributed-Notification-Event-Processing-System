import time
import json
from .redis_client import redis_client


def is_rate_limited(user_id, capacity=5, refill_rate=0.1):
    """
    capacity: max tokens in bucket
    refill_rate: tokens per second
    """

    key = f"token_bucket:{user_id}"
    now = time.time()

    bucket = redis_client.get(key)

    if bucket:
        bucket = json.loads(bucket)
        tokens = bucket["tokens"]
        last_refill = bucket["last_refill"]
    else:
        tokens = capacity
        last_refill = now

    # Step 1: Refill tokens
    elapsed = now - last_refill
    refill = elapsed * refill_rate

    tokens = min(capacity, tokens + refill)

    # Step 2: Check if request allowed
    if tokens < 1:
        # save state
        redis_client.set(key, json.dumps({
            "tokens": tokens,
            "last_refill": now
        }))
        return True  # rate limited

    # Step 3: Consume token
    tokens -= 1

    # Step 4: Save updated state
    redis_client.set(key, json.dumps({
        "tokens": tokens,
        "last_refill": now
    }))

    return False



##################################################################################################
# Fixed window approach for rate limiting
# from .redis_client import redis_client

# def is_rate_limited(user_id, limit=5, window=60):
#     key = f"rate_limit:{user_id}"

#     current = redis_client.get(key)

#     if current and int(current) >= limit:
#         return True

#     # increment counter
#     redis_client.incr(key)

#     # set expiry only first time
#     if current is None:
#         redis_client.expire(key, window)

#     return False