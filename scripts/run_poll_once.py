"""One-shot official news polling command."""

from __future__ import annotations

import asyncio

from backend.modules.translator.services.news_polling_service import NewsPollingService


async def main() -> None:
    """Run one polling cycle and print a human-readable summary."""
    result = await NewsPollingService().poll_once()
    print(
        f"Fetched: {result.fetched}, created: {result.created}, "
        f"skipped: {result.skipped}, failed: {result.failed}"
    )
    for error in result.errors:
        print(f"  - {error}")


if __name__ == "__main__":
    asyncio.run(main())
