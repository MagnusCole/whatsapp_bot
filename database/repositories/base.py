from typing import Generic, TypeVar, Type
from drizzle_orm import PostgresDatabase
from ..schema import Table

T = TypeVar('T', bound=Table)

class BaseRepository(Generic[T]):
    def __init__(self, db: PostgresDatabase, model: Type[T]):
        self.db = db
        self.model = model

    async def create(self, **kwargs) -> T:
        return await self.db.insert(self.model).values(**kwargs).returning()

    async def get_by_id(self, id: int) -> T:
        return await self.db.select(self.model).where(self.model.id == id).first()