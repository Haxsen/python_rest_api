from fastapi import APIRouter, HTTPException
from sqlalchemy.future import select

from app.schemas import DepositOrWithdrawRequestRust, CheckBalanceRequestRust, RegisterUser
from app.models import async_session, UserModel, InvestedModel
from app.services.rust_client import deposit, withdraw, check_balance

router = APIRouter()

# Register a user
@router.post("/register")
async def register_user(request: RegisterUser):
    async with async_session() as session:
        try:
            # Check user
            user_query = select(UserModel).where(UserModel.userid == request.userid)
            result = await session.execute(user_query)
            user = result.scalar_one_or_none()

            if user:
                raise HTTPException(status_code=500, detail="User already exists.")

            # Record the user
            user_record = UserModel(userid=request.userid, email=request.email, userprivatekey=request.userprivatekey)
            session.add(user_record)

            await session.commit()
            return {"status": "success", "userid_registered": user_record.userid}
        except Exception as e:
            await session.rollback()
            print(f"Unexpected error: {e}")
            raise HTTPException(status_code=500, detail="An unexpected error occurred")

# Endpoint to invest ETH
@router.post("/deposit")
async def deposit_eth(request: DepositOrWithdrawRequestRust):
    async with async_session() as session:
        try:
            # Pick user's private address
            user_query = select(UserModel).where(UserModel.userid == request.userid)
            result = await session.execute(user_query)
            user = result.scalar_one_or_none()

            userprivatekey = user.userprivatekey

            # Send request to Rust service
            response = await deposit(userprivatekey, request.amount)
            if response is None:
                raise HTTPException(status_code=500, detail="Failed to deposit on blockchain")

            # Record the investment
            stmt = select(InvestedModel).filter(InvestedModel.userid == request.userid)
            result = await session.execute(stmt)
            invested_record = result.scalars().first()

            if invested_record:
                invested_record.investedwei += request.amount
            else:
                invested_record = InvestedModel(userid=request.userid, investedwei=request.amount)
                session.add(invested_record)

            await session.commit()
            return {"status": "success", "amount_invested": invested_record.investedwei}
        except Exception as e:
            await session.rollback()
            print(f"Unexpected error: {e}")
            raise HTTPException(status_code=500, detail="An unexpected error occurred")

# Endpoint to invest ETH
@router.post("/withdraw")
async def withdraw_eth(request: DepositOrWithdrawRequestRust):
    async with async_session() as session:
        try:
            # Pick user's private address
            user_query = select(UserModel).where(UserModel.userid == request.userid)
            result = await session.execute(user_query)
            user = result.scalar_one_or_none()

            userprivatekey = user.userprivatekey

            # Send request to Rust service
            response = await withdraw(userprivatekey, request.amount)
            if response is None:
                raise HTTPException(status_code=500, detail="Failed to deposit on blockchain")

            stmt = select(InvestedModel).filter(InvestedModel.userid == request.userid)
            result = await session.execute(stmt)
            invested_record = result.scalars().first()

            invested_record.investedwei -= request.amount

            await session.commit()
            return {"status": "success", "amount_withdrawn": request.amount, "remaining_balance": invested_record.investedwei}
        except Exception as e:
            await session.rollback()
            print(f"Unexpected error: {e}")
            raise HTTPException(status_code=500, detail="An unexpected error occurred")

# Endpoint to invest ETH
@router.post("/check_balance")
async def check(request: CheckBalanceRequestRust):
    async with async_session() as session:
        try:
            # Pick user's private address
            user_query = select(UserModel).where(UserModel.userid == request.userid)
            result = await session.execute(user_query)
            user = result.scalar_one_or_none()

            userprivatekey = user.userprivatekey

            # Send request to Rust service
            response = await check_balance(userprivatekey)
            print(response)
            if response is None:
                raise HTTPException(status_code=500, detail="Failed to query balance on blockchain")

            return {"status": "success", "balance": response}
        except Exception as e:
            await session.rollback()
            print(f"Unexpected error: {e}")
            raise HTTPException(status_code=500, detail="An unexpected error occurred")
