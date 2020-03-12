# -*- coding: utf-8 -*-
"""
商户登录、登出模块
"""
from fastapi import APIRouter

from decorators import log_filter

router = APIRouter()


@router.post("/login")
@log_filter
def login(name: str):
    return name


@router.post("/logout")
def login():
    return "logout"
