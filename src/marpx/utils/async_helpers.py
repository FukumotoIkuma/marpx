"""Async/sync bridging utilities."""

import asyncio
import concurrent.futures
from collections.abc import Coroutine
from typing import TypeVar

T = TypeVar("T")


def run_coroutine_sync(coro: Coroutine[object, object, T]) -> T:
    """Run a coroutine from synchronous code, handling nested event loops."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    # Already inside an event loop — run in a new thread to avoid nesting
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(asyncio.run, coro).result()
