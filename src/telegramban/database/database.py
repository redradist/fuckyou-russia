from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, String, insert
from sqlalchemy import update as sqlalchemy_update
from sqlalchemy.future import select
from sqlalchemy.orm import declarative_base

Base = declarative_base()


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


class UserSession(Base, ModelAdmin):
    __tablename__ = "user-sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, unique=True)
    name = Column(String)
    lang = Column(String)
    phone = Column(String, unique=True)
    session = Column(String, unique=True)

    # required in order to acess columns with server defaults
    # or SQL expression defaults, subsequent to a flush, without
    # triggering an expired load
    __mapper_args__ = {"eager_defaults": True}

    def __repr__(self):
        return (
            f"<{self.__class__.__name__}("
            f"id={self.id}, "
            f"user_id={self.user_id}, "
            f"name={self.name}, "
            f"phone={self.phone}"
            f")>"
        )

    @classmethod
    async def filter_by_name(cls, name):
        query = select(cls).where(cls.name == name)
        sessions = await async_db_session.execute(query)
        return sessions.scalars().all()

    @classmethod
    async def filter_by_phone(cls, phone):
        query = select(cls).where(cls.phone == phone)
        sessions = await async_db_session.execute(query)
        return sessions.scalars().all()

    @classmethod
    async def get_all(cls):
        query = select(cls)
        sessions = await async_db_session.execute(query)
        return sessions.scalars().all()


class AsyncDatabaseSession:
    def __init__(self):
        self._engine = create_async_engine(
            "postgresql+asyncpg://postgres:postgres@localhost/postgres",
            echo=True,
        )
        self._session = sessionmaker(
            self._engine,
            expire_on_commit=False,
            class_=AsyncSession
        )()

    def __getattr__(self, name):
        return getattr(self._session, name)

    async def create_all(self):
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_all(self):
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)


async_db_session = AsyncDatabaseSession()
