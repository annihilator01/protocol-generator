from decimal import Decimal
from sqlmodel import text

from .base import BaseRepo


class TVLHistoryRepo(BaseRepo):
    CALCULATE_HISTORY_SQL = """
        INSERT INTO tvl_history(
            protocol_token_id,
            created_at_block,
            amount,
            amount_usd,
            created_at
        )
        SELECT
            abh.protocol_token_id,
            abh.created_at_block,
            SUM(abh.amount) AS amount,
            UNNEST(MIN(usd_price_ticks.usd_price)) * SUM(abh.amount)
                AS amount_usd,
            UNNEST(MIN(usd_price_ticks.created_at)) AS created_at
        FROM account_balance_history abh
        JOIN protocol_token pt ON abh.protocol_token_id = pt.id,
        LATERAL (
            SELECT
                ARRAY_AGG(tp.usd_price ORDER BY tp.created_at) AS usd_price,
                ARRAY_AGG(tp.created_at ORDER BY tp.created_at) AS created_at
            FROM token_price tp
            WHERE
                tp.token_id = pt.token_id
                AND (
                    tp.created_at - abh.created_at
                    BETWEEN INTERVAL '0' AND INTERVAL '1 hour'
                )
        ) usd_price_ticks
        WHERE pt.protocol_id = :protocol_id
        GROUP BY
            abh.protocol_token_id,
            abh.created_at_block;
    """

    GET_CURRENT_PROTOCOL_PRICE_SQL = """
        WITH block AS (
            SELECT MAX(tvl.created_at_block) AS max_block_num
            FROM tvl_history tvl
            JOIN protocol_token pt ON tvl.protocol_token_id = pt.id
            WHERE pt.protocol_id = :protocol_id
        )
        SELECT
            SUM(amount_usd)
        FROM tvl_history tvl
        JOIN protocol_token pt ON tvl.protocol_token_id = pt.id
        WHERE
            pt.protocol_id = :protocol_id
            AND tvl.created_at_block = (SELECT max_block_num FROM block);
    """

    async def calculate_history_by_protocol_id(self, protocol_id: int):
        await self.session.execute(
            text(self.CALCULATE_HISTORY_SQL),
            {"protocol_id": protocol_id},
        )

    async def get_current_protocol_price(
        self,
        protocol_id: int
    ) -> Decimal | None:
        result = await self.session.execute(
            text(self.GET_CURRENT_PROTOCOL_PRICE_SQL),
            {"protocol_id": protocol_id},
        )
        return result.one_or_none()
