# -*- coding: utf-8 -*-
"""
安全校验工具类
"""
import time
import jwt
import starlette.status
from datetime import datetime, timedelta
from fastapi import Cookie, HTTPException
from passlib.context import CryptContext

from config import SECRET_KEY, ALGORITHM
from utils import logger

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(*, data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=12)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt.decode()


def verify_token(token):
    token = token.encode()
    credentials_exception = HTTPException(
        status_code=starlette.status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    merchant_id: int = payload.get("merchant_id")
    if merchant_id is None:
        raise credentials_exception
    return merchant_id


def get_login_merchant(x_token: str = Cookie(...)):
    """
    从token获取当前登录用户id
    :param x_token:
    """
    # 校验登录token
    if x_token is None or x_token == "":
        raise HTTPException(status_code=401, detail="请先登录!")
    try:
        cur_merchant_id = verify_token(x_token)
        return cur_merchant_id
    except jwt.ExpiredSignatureError as e:
        logger.error(str(e))
        raise HTTPException(status_code=403, detail="登录态过期, 请重新登录!")
    except jwt.PyJWTError as e:
        logger.error(str(e))
        raise HTTPException(status_code=403, detail="无效token!")
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=401, detail="非法请求!")


if __name__ == "__main__":
    access_token_expires = timedelta(seconds=3)
    access_token = create_access_token(
        data={"merchant_id": 1}, expires_delta=access_token_expires
    )
    print(type(access_token))
    print(access_token)
    time.sleep(4)
    print(verify_token(access_token))
