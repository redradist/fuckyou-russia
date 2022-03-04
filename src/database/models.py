from sqlalchemy import Column, Integer, String
from sqlalchemy import update as sqlalchemy_update
from sqlalchemy.future import select

from src.database.database import Base, async_db_session


class ModelAdmin:
    @classmethod
    async def create(cls, **kwargs):
        async_db_session.add(cls(**kwargs))
        await async_db_session.commit()

    @classmethod
    async def update(cls, id, **kwargs):
        query = (
            sqlalchemy_update(cls)
            .where(cls.id == id)
            .values(**kwargs)
            .execution_options(synchronize_session="fetch")
        )

        await async_db_session.execute(query)
        await async_db_session.commit()

    @classmethod
    async def get(cls, id):
        query = select(cls).where(cls.id == id)
        results = await async_db_session.execute(query)
        (result,) = results.one()
        return result


class TelegramSession(Base, ModelAdmin):
    __tablename__ = "telegram-sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(String, unique=True)
    user_session = Column(String)

    # required in order to acess columns with server defaults
    # or SQL expression defaults, subsequent to a flush, without
    # triggering an expired load
    __mapper_args__ = {"eager_defaults": True}

    def __repr__(self):
        return (
            f"<{self.__class__.__name__}("
            f"id={self.id}, "
            f"user_name={self.user_name}, "
            f"user_session={self.user_session}, "
            f")>"
        )

    @classmethod
    async def filter_by_user_name(cls, user_name):
        query = select(cls).where(cls.user_name == user_name)
        sessions = await async_db_session.execute(query)
        return sessions.scalars().all()
