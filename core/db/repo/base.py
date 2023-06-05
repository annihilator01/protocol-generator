from sqlalchemy.ext.asyncio import AsyncSession

from core.db.model import BaseSQLModel


class BaseRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_all(
        self,
        objects: list[BaseSQLModel],
        with_commit: bool = False,
    ):
        self.session.add_all(objects)
        if with_commit:
            await self.session.commit()
