# -*- coding: utf-8 -*-
import redis
from config import redis_config

pool = redis.ConnectionPool(host=redis_config["host"], port=redis_config["port"], encoding='utf-8',
                            decode_responses=True)
redis_client = redis.Redis(connection_pool=pool, password=redis_config["passwd"])

