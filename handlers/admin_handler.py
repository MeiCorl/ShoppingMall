# -*- coding: utf-8 -*-
"""
管理员模块
"""
from fastapi import APIRouter
router = APIRouter()


@router.get("/admin/me")
def show_me():
    return "Hello"
