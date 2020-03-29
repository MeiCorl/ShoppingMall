# -*- coding: utf-8 -*-
app_log_path = "logs/app.log"
msg_log_path = "logs/msg.log"


db_config = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "passwd": "",
    "dbname": "shopping_mall"
}

redis_config = {
    "host": "localhost",
    "port": 6379,
    "passwd": ""
}

app_config = {
    "port": 6035,
    "backlog": 100,
    "reload": True,
    "log_level": "debug",
    "access_log": True,
    "use_colors": True,
    "host": "127.0.0.1"
}

socket_config = {
    "host": "127.0.0.1",
    "port": 6789
}

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

# merchants_listener_topic用于通知商户后端接收新消息， merchants_message_queue作为商户后端消息队列
merchants_listener_topic = "merchants_listener"
merchants_message_queue = "merchants_message_queue"

# miniapp_listener_topic用于通知小程序后端接收新消息， miniapp_message_queue作为小程序后端消息队列
miniapp_listener_topic = "miniapp_listener"
miniapp_message_queue = "miniapp_message_queue"
