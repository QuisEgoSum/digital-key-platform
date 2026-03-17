from redis import asyncio as aioredis

from config.runtime.loader import get_config

_config = get_config()

redis = aioredis.from_url(_config.infra.persistence.databases.redis.uri)
