#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=W0102,E0712,C0103,R0903

"""K/V Distributed Leader Election"""

import os, time, uuid
import redis

###############################################################################
#
# DATA STRUCTURES AND VARIABLES
#
###############################################################################

# Environment variables define key parameters:
# - The Redis key used for the distributed lock
# - Lock expiration time in milliseconds
# - Renewal frequency
# - Sleep time between standby check attempts
LOCK_KEY = os.environ["LOCK_KEY"]
TTL_MS = int(os.getenv("LOCK_TTL_MS", "15000"))
RENEW_EVERY_MS = int(os.getenv("LOCK_RENEW_EVERY_MS", "5000"))
STANDBY_SLEEP_MS = int(os.getenv("STANDBY_SLEEP_MS", "2000"))

# A unique identifier for this instance (used to identify the lock owner)
INSTANCE_ID = os.getenv("INSTANCE_ID") or str(uuid.uuid4())

# Create a Redis connection using host and port from environment or defaults
r = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    socket_connect_timeout=1.0,
    socket_timeout=1.0,
    retry_on_timeout=True,
)

# Lua script for safely renewing the lock; avoids extending someone else's lock
RENEW_LUA = """
if redis.call("GET", KEYS[1]) == ARGV[1] then
  return redis.call("PEXPIRE", KEYS[1], ARGV[2])  -- Extend lock TTL if still owned
else
  return 0  -- Renew fails if another instance owns or deleted the key
end
"""
# Register the Lua script with Redis
renew_script = r.register_script(RENEW_LUA)

###############################################################################
#
# SUPPORT FUNCTIONS
#
###############################################################################


def try_acquire() -> bool:
    """
    Try to obtain the distributed lock.
    """
    try:
        # SET with NX (only if not exists) and PX (expire in TTL_MS)
        return bool(r.set(LOCK_KEY, INSTANCE_ID, nx=True, px=TTL_MS))
    except redis.RedisError:
        return False  # if Redis is unreachable or other errors occur


def renew() -> bool:
    """
    Try to renew the lock if still held by this instance.
    """
    try:
        # Run Lua script to safely refresh TTL if we still own the lock
        return int(renew_script(keys=[LOCK_KEY], args=[INSTANCE_ID, str(TTL_MS)])) == 1
    except redis.RedisError:
        return False  # if renewal fails on Redis errors


def open_telnet():
    """
    Blocking task initiatied.
    """
    # Placeholder: start Telnet session or equivalent leader-only functionality
    print("OPEN TELNET (leader)")


def close_telnet():
    """
    Blocking task stopped.
    """
    # Placeholder: terminate Telnet session quickly when losing leadership
    print("CLOSE TELNET (standby)")


###############################################################################
#
# APPLICATION MAIN
#
###############################################################################


def main() -> None:
    """
    Main loop: attempts to become leader or renew the lock periodically. If it's
    not possible, go to sleep.
    """
    # Track leadership state within the loop scope
    is_leader = False

    while True:
        if not is_leader:

            # If not leader, try to acquire lock
            if try_acquire():
                # Acquired lock, this instance becomes leader, therefore,
                # start leader duties and or blocking tasks
                is_leader = True
                open_telnet()
            else:
                # Lock not acquired or Redis down, therefore go to standby mode.
                # Ensure leader functions (the are blocking) are closed and then
                # wait before retrying
                close_telnet()
                time.sleep(STANDBY_SLEEP_MS / 1000.0)
        else:
            # Already leader, therefore try to renew periodically. During duty
            # renewal failed, therefore lost leadership or Redis unavailable;
            # revert role, stop leader operations (locking tasks), hang on
            # during a short delay before retry, during which. duty might fail
            # again or the renewal might succeed, in which case continue with
            # leadership
            if not renew():
                is_leader = False
                close_telnet()
                time.sleep(1)
            else:
                time.sleep(RENEW_EVERY_MS / 1000.0)


###############################################################################
#
# APPLICATION ENTRY POINT
#
###############################################################################

if __name__ == "__main__":
    """
    Application entry point block
    """
    main()
