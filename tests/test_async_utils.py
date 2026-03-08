"""Tests for marpx.async_utils."""

import pytest

from marpx.async_utils import run_coroutine_sync


async def _double(n: int) -> int:
    return n * 2


class TestRunCoroutineSync:
    """Tests for run_coroutine_sync."""

    def test_no_running_loop(self) -> None:
        """Should work via asyncio.run when no event loop is running."""
        result = run_coroutine_sync(_double(21))
        assert result == 42

    def test_returns_coroutine_result(self) -> None:
        """Should correctly return the coroutine's result."""
        result = run_coroutine_sync(_double(5))
        assert result == 10

    @pytest.mark.asyncio
    async def test_inside_running_loop(self) -> None:
        """Should work via ThreadPoolExecutor when called inside a running loop."""
        result = run_coroutine_sync(_double(7))
        assert result == 14
