from redis import asyncio as aioredis

from config import config

redis = aioredis.from_url(config.infra.persistence.databases.redis.uri)
