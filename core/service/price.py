from decimal import Decimal
from typing import TYPE_CHECKING

from core.db.repo import TVLHistoryRepo

if TYPE_CHECKING:
    from core.shell.model import GetCurrentDepositCommandOptions


class ProtocolPriceService:
    def __init__(self, tvl_history_repo: TVLHistoryRepo):
        self.tvl_history_repo = tvl_history_repo

    async def get_protocol_price(
        self,
        options: "GetCurrentDepositCommandOptions",
    ) -> Decimal:
        protocol_price = (
            await self.tvl_history_repo.get_current_protocol_price(
                protocol_id=options.protocol,
            )
        )

        if not protocol_price:
            raise ValueError(
                "There is no such protocol. Price cannot be defined."
            )

        return protocol_price[0]
