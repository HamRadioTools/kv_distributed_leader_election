#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=W0102,E0712,C0103,R0903

"""K/V Distributed Leader Election"""

__updated__ = "2025-12-14 01:24:24"

import os
from dotenv import load_dotenv, find_dotenv

# Load variables from an optional .env file for local development.
load_dotenv(find_dotenv())


def str_to_bool(value: str | None, default: bool = True) -> bool:
    """
    Convert truthy / falsy strings to booleans, falling back to default when unset.
    """
    if value is None:
        return default
    return value.lower() in ("1", "true", "yes", "y", "t")


def get_int(name: str, default: int) -> int:
    """
    Fetch an environment variable and coerce it to int with a default.
    """
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError as exc:
        msg = f"Environment variable {name} must be an integer, got '{raw}'"
        raise ValueError(msg) from exc


def get_float(name: str, default: float) -> float:
    """
    Fetch an environment variable and coerce it to float with a default.
    """
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError as exc:
        msg = f"Environment variable {name} must be a float, got '{raw}'"
        raise ValueError(msg) from exc


def get_required(name: str) -> str:
    """
    Fetch a mandatory environment variable or raise a RuntimeError.
    """
    value = os.getenv(name)
    if value is None or value.strip() == "":
        raise RuntimeError(f"Environment variable {name} is required for startup")
    return value


def get_config() -> dict:
    """
    Return the 12-factor configuration as a dict used by the leader election loop.
    """

    # --- Leader lock parameters ---
    lock_key = get_required("LOCK_KEY")
    lock_ttl_ms = get_int("LOCK_TTL_MS", default=15000)
    lock_renew_every_ms = get_int("LOCK_RENEW_EVERY_MS", default=5000)
    standby_sleep_ms = get_int("STANDBY_SLEEP_MS", default=2000)

    # --- Redis connection ---
    redis_host = os.getenv("REDIS_HOST", "redis")
    redis_port = get_int("REDIS_PORT", default=6379)
    redis_db = get_int("REDIS_DB", default=0)
    redis_password = os.getenv("REDIS_PASSWORD")

    return {
        # --- Service identity ---
        "INSTANCE_ID": os.getenv("INSTANCE_ID"),
        # --- Locking ---
        "LOCK_KEY": lock_key,
        "LOCK_TTL_MS": lock_ttl_ms,
        "LOCK_RENEW_EVERY_MS": lock_renew_every_ms,
        "STANDBY_SLEEP_MS": standby_sleep_ms,
        # --- Redis client ---
        "REDIS_HOST": redis_host,
        "REDIS_PORT": redis_port,
        "REDIS_DB": redis_db,
        "REDIS_PASSWORD": redis_password,
        "REDIS_SOCKET_CONNECT_TIMEOUT": get_float("REDIS_SOCKET_CONNECT_TIMEOUT", 1.0),
        "REDIS_SOCKET_TIMEOUT": get_float("REDIS_SOCKET_TIMEOUT", 1.0),
        "REDIS_RETRY_ON_TIMEOUT": str_to_bool(
            os.getenv("REDIS_RETRY_ON_TIMEOUT", "true"), default=True
        ),
    }


if __name__ == "__main__":
    # Handy for quick inspection
    from pprint import pprint

    pprint(get_config())
