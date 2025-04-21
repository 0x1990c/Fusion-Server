import os
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from database import AsyncSessionLocal
from app.Utils.Auth import authenticate_user, create_access_token, get_password_hash, get_current_user
from app.Utils.sendgrid import send_mail, send_approve_email
import secrets
import os

from app.Model.CaseModel import TimeRange
from app.Model.CaseModel import FilterCondition

import app.Utils.database_handler as crud
import app.Utils.Auth as Auth

from typing import Annotated

from dotenv import load_dotenv

load_dotenv()
router = APIRouter()

# Dependency to get the database session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


@router.post("/getCases")
async def getCases(timeRange: TimeRange, db: Session = Depends(get_db)):
    try:
        print("timeRange : ", timeRange)
        cases = await crud.get_cases(db, timeRange)
        return {"cases": cases}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/getCounties")
async def getCounties(db: Session = Depends(get_db)):
    try:
        counties = await crud.get_counties(db)
        return {"counties": counties}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/getData")
async def getData(filterCondition: FilterCondition, db: Session = Depends(get_db)):
    try:
        cases = await crud.get_data(db, filterCondition)
        return {"cases": cases}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))