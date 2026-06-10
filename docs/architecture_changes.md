# Architecture Changes: Redis Polling with GraphQL Subscriptions

This document details the changes made to transition the application to an asynchronous, polling-based GraphQL subscription architecture relying strictly on Redis `HSET` and `HGETALL` operations.

## Overview
Instead of utilizing Redis Pub/Sub, the system now uses a **Producer-Worker-Subscriber** pattern backed by basic Redis hashes:
1. **Producer (GraphQL Mutation)**: Receives raw data, saves an initial `"pending"` status to a Redis hash, fires off a background worker task, and immediately responds with a Task ID.
2. **Worker (Background Task)**: Processes the task asynchronously (using `DataPreprocess`) and updates the Redis hash with the `completed` status and processed fields.
3. **Subscriber (GraphQL Subscription)**: Polls the Redis hash at regular intervals (1 second) to check the task status. When the status changes to `"completed"`, it yields the finalized response back to the client.

---

## Breakdown of File Changes

### 1. `src/application/worker.py` (New)
**What it does:**
This file handles the background processing logic. It defines the `process_worker` asynchronous function which:
- Accepts a `task_id`, the validated `RawDataModel`, and the `RedisAdapter`.
- Instantiates the `DataPreprocess` service to perform domain logic calculations.
- Augments the processed data with the `task_id` and a `status` of `"completed"`.
- Uses `redis_adapter.update()` (which maps to `HSET` under the hood) to update the Redis cache.
- Has error handling built-in to catch exceptions and update the status to `"failed"` if processing crashes.

### 2. `src/adapters/graphql/schema.py` (Modified)
**What it does:**
This file defines the entire GraphQL contract using `strawberry`. Key updates include:
- **`RawDataInput`**: A Strawberry input type so users can provide mutation payloads matching the domain `RawDataModel`.
- **`ProcessedData` & `TaskStatusResponse`**: Strawberry output types corresponding to the response formats.
- **`Mutation.processData`**: 
  - Retrieves the `redis_adapter` from the GraphQL context.
  - Generates a `uuid4` task identifier.
  - Calls `RedisAdapter.set()` to initialize the status to `"pending"`.
  - Dispatches `asyncio.create_task(process_worker(...))` so the FastAPI event loop processes the data in the background without blocking the mutation.
- **`Subscription.dataStatus`**: 
  - An asynchronous generator that uses `while True` combined with `asyncio.sleep(1)`.
  - It repeatedly fetches the task state using `RedisAdapter.get()` (`HGETALL`).
  - Upon detecting `status == "completed"`, it parses the returned string values back to proper Python primitives, yields the `ProcessedData`, and exits the loop.

### 3. `src/main.py` (Modified)
**What it does:**
This file serves as the core entrypoint for the FastAPI application, bridging FastAPI, Strawberry, and Redis.
- **Redis Initialization**: Initializes the global `redis.Redis()` client. Crucially, sets `decode_responses=True` so `HGETALL` automatically returns parsed strings instead of raw byte strings, simplifying data retrieval in the Strawberry resolver.
- **GraphQL Router**: Mounts the Strawberry schema on the `/graphql` route.
- **Context Injection**: Uses `context_getter` so that any GraphQL resolver (Mutation or Subscription) can access the `redis_adapter` securely via `info.context`.
- **Lifespan Management**: Uses `@asynccontextmanager` to ensure the Redis connection gracefully disconnects when the FastAPI server terminates.

---

## How to Test
You can start the server locally:
```bash
uv run uvicorn src.main:app --reload
```

1. Subscribe to a task ID in GraphQL Playground (using the `dataStatus` subscription).
2. Execute the `processData` mutation in a separate tab.
3. Take the returned `taskId` from the mutation and use it in your subscription tab to see the system instantly resolve the payload once the background worker finishes.
