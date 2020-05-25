#!python3
from app.db.mongo import MongoDB
from app.conf import config


def mongo():
    return MongoDB(config.MONGO_HOST, config.MONGO_PORT, config.MONGO_DB_NAME)
