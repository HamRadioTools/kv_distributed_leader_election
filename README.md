# Distributed leader election (for microservices) using k/v stores

This code implements a "distributed leader election" operational model leveraging the `fail-closed` architecture software pattern. This pattern can be implemented with code and supported on regular key/values stored in Redis or DragonFly (same Redis API) working as a locking mechanism. This locking mechanism ensures the following actions:

- Only one instance, of a single microservice type, can hold the LOCK_KEY (the leader) at a time.
- The leader periodically renews its lock; if it fails in doing so, another instance can take over the leadership.

## Meaning of `fail-closed` architecture software pattern

The code has been architected using the `fail-closed` architecture software pattern, which design assumes dependencies will sometimes break (for example, Redis going down) and defines that, in those cases, the system should stop doing the “dangerous” or critical thing rather than continue in an incorrect or inconsistent state. 

By implementing this pattern it's posible to ensure high availability in a system where only one node should perform a certain action.

## How it works in practice

- When an instance cannot acquire the lock (because another instance holds it or because Redis is unreachable), it calls close_telnet() and goes to sleep as standby.
- When the instance is leader but lock renewal fails, it immediately drops leadership, closes locking task and waits before trying again.

In both cases, failure leads to “closed” behavior: no locking task can run safely, no leader work, and the instances stay passive until it can prove it's safe to get the lock again, that means Redis is up again to signal who should be the leader.  

**_This is the essence of `fail-close`: default to off/standby when not 100% sure things are correct._**
