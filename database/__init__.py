from tortoise import Tortoise
import logging as log


async def init_database() -> None:
    await Tortoise.init(
        db_url=f"sqlite://database/db.sqlite",
        modules={
            "models": [
                "database.models.user",
                "database.models.reports",
                "database.models.lots",
                "database.models.lots_cache",
            ]
        },
    )
    await Tortoise.generate_schemas()
    log.info("database initialized")


async def close_database():
    await Tortoise.close_connections()




