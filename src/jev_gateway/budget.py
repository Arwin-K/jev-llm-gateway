"""Conservative process-local admission control for paid frontier requests."""

import asyncio

from .config import Settings


class BudgetExceeded(RuntimeError):
    pass


class FrontierBudget:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.lock = asyncio.Lock()
        self.requests = 0
        self.reserved_tokens = 0
        self.reserved_usd = 0.0

    async def reserve(self, messages: list[dict], max_output_tokens: int):
        if not self.settings.frontier_enabled:
            raise BudgetExceeded("frontier is disabled")
        # Four units per code point plus framing overhead is deliberately high,
        # but provider tokenization/billing may differ. See budget limitations.
        input_units = 4 * sum(len(message["content"]) for message in messages) + 32 * len(messages)
        tokens = input_units + max_output_tokens
        usd = (input_units * self.settings.frontier_input_usd_per_million +
               max_output_tokens * self.settings.frontier_output_usd_per_million) / 1_000_000
        async with self.lock:
            if (self.requests + 1 > self.settings.frontier_max_requests or
                self.reserved_tokens + tokens > self.settings.frontier_max_tokens or
                self.reserved_usd + usd > self.settings.frontier_max_usd):
                raise BudgetExceeded("frontier request exceeds configured process budget")
            self.requests += 1
            self.reserved_tokens += tokens
            self.reserved_usd += usd
        return {"reserved_tokens": tokens, "reserved_usd": usd}
