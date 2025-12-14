# Distributed leader election (for microservices) using k/v stores

This code servers as a template demonstrating how to handle a locking task this is connecting a destination Telnet host while implementing a "distributed leader election" operational model leveraging the `fail-closed` architecture software pattern. 

This pattern can be implemented with code and supported on regular key/values stored in Redis or DragonFly (same Redis API,no need for Redis Streams or any other advance module) working as a locking mechanism. This locking mechanism ensures the following actions:

- Only one instance, out of potentially many of a single microservice type bein run, can hold the LOCK_KEY (the leader) at a time, a typical scenario en Docker Swarm, K8s and/or HashiCopr Nomad orchestrators. 
- The leader periodically renews its lock; if it fails in doing so, another instance can take over the leadership.

## Meaning of `fail-closed` architecture software pattern

The code has been architected using the `fail-closed` architecture software pattern, which design assumes dependencies will sometimes break (for example, Redis going down) and defines that, in those cases, the system should stop doing the “dangerous” or critical thing rather than continue in an incorrect or inconsistent state. 

By implementing this pattern **it's posible to ensure high availability in a system where only one node should perform a certain action**.

## How it works in practice

- When an instance cannot acquire the lock (because another instance holds it or because Redis is unreachable), it calls close_telnet() and goes to sleep as standby.
- When the instance is leader but lock renewal fails, it immediately drops leadership, closes locking task and waits before trying again.

In both cases, failure leads to “closed” behavior: no locking task can run safely, no leader work, and the instances stay passive until it can prove it's safe to get the lock again, that means Redis is up again to signal who should be the leader.  

**_This is the essence of `fail-close`: default to off/standby when not 100% sure things are correct._**

## Strengths of this design

1. **Atomic operations**: The code uses Redis' atomic SET NX command for lock acquisition and a Lua script for renewal, which prevents race conditions and ensures consistency.

2. **Optimized Redis connection**: The Redis connection is configured with appropriate timeouts and retry settings:
   ```python
   socket_connect_timeout=1.0,
   socket_timeout=1.0,
   retry_on_timeout=True
   ```
   This prevents the application from hanging indefinitely if Redis is unresponsive.

3. **Error handling**: The code properly handles Redis errors in both the `try_acquire()` and `renew()` functions, preventing crashes when Redis is unavailable.

4. **Configurable parameters**: Key parameters like TTL, renewal frequency, and sleep times are configurable via environment variables, allowing for tuning without code changes.

5. **Unique instance ID**: Using UUID, ensures each instance has a unique identifier, which is essential for proper lock ownership.

## Areas for improvement

1. **Sleep timing**: The code uses `time.sleep()` with fixed intervals. This could be inefficient in some scenarios:
   - In line 124, it sleeps for a fixed `STANDBY_SLEEP_MS` regardless of how long until the current lock expires
   - In line 137, it sleeps for `RENEW_EVERY_MS` without accounting for how long the renewal operation took

2. **Lack of backoff strategy**: There's no exponential backoff when Redis is unavailable, which could lead to excessive connection attempts during outages.

3. **No graceful shutdown**: There's no handling for graceful shutdown (e.g., via signals), which could leave resources in an inconsistent state.

4. **Single Redis Instance**: The code connects to a single Redis instance, creating a single point of failure for the leader election mechanism.
