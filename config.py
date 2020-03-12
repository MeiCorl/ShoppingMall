# -*- coding: utf-8 -*-

log_path = "logs/app.log"

# 生产环境
# db_config = {
#     "host": "100.89.224.11",
#     "port": 15187,
#     "user": "root",
#     "passwd": "y3@K15mhLR",
#     "dbname": "db_cage"
# }
db_config = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "passwd": "",
    "dbname": "shopping_mall"
}

app_config = {
    "port": 6035,
    "backlog": 100,
    "reload": True,
    "log_level": "debug",
    # "log_config": "./logging_config.ini",
    "access_log": True,
}

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24
