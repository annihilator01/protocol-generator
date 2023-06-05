from sqlmodel import select

from core.db.model import ProtocolToken

from .base import BaseRepo


class ProtocolTokenRepo(BaseRepo):
    async def get_protocol_token_by_protocol_id(
        self,
        protocol_id: int,
    ) -> list[ProtocolToken]:
        result = await self.session.execute(
            select(ProtocolToken)
            .where(ProtocolToken.protocol_id == protocol_id)
        )

        return result.scalars().all()
