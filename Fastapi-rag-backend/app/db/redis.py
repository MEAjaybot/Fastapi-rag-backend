# app/db/redis.py
import redis
import os
from dotenv import load_dotenv

redis_client = redis.Redis(
    host="localhost", 
    port=6379, 
    db=0, 
    decode_responses=True
)