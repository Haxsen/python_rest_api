from fastapi import APIRouter, HTTPException
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from app.models import RestakeOperation, User, async_session
from app.services.history import record_restake_history
from app.services.rust_client import initiate_restake_on_chain
from app.schemas import RestakeRequest, ConfirmRequest

router = APIRouter()


# Endpoint to initiate restake operation
@router.post("/restake")
async def initiate_restake(request: RestakeRequest):
    async with async_session() as session:
        try:
            # Check if user exists
            user_query = select(User).where(User.id == request.user_id)
            result = await session.execute(user_query)
            user = result.scalar_one_or_none()

            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # Create new restake operation
            new_restake = RestakeOperation(user_id=request.user_id, amount=request.amount, status="pending")
            session.add(new_restake)
            await session.commit()

            # Send request to Rust service
            response = await initiate_restake_on_chain(request.user_id, request.amount)
            if response is None or response.status_code != 200:
                raise HTTPException(status_code=500, detail="Failed to initiate restake on blockchain")

            return {"message": "Restake initiated", "operation_id": new_restake.id}

        except IntegrityError:
            await session.rollback()
            raise HTTPException(status_code=400, detail="Database integrity error")
        except Exception as e:
            await session.rollback()
            print(f"Unexpected error: {e}")
            raise HTTPException(status_code=500, detail="An unexpected error occurred")


# Endpoint to check status of restake operation
@router.get("/restake/{operation_id}")
async def check_restake_status(operation_id: int):
    async with async_session() as session:
        try:
            # Query the database for the specific restake operation
            operation_query = select(RestakeOperation).where(RestakeOperation.id == operation_id)
            result = await session.execute(operation_query)
            operation = result.scalar_one_or_none()

            if not operation:
                raise HTTPException(status_code=404, detail="Restake operation not found")

            return {"operation_id": operation.id, "status": operation.status, "amount": operation.amount}

        except Exception as e:
            print(f"Unexpected error: {e}")
            raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.post("/confirm-restake")
async def confirm_restake(request: ConfirmRequest):
    async with async_session() as session:
        try:
            operation_query = select(RestakeOperation).where(RestakeOperation.id == request.operation_id)
            result = await session.execute(operation_query)
            operation = result.scalar_one_or_none()

            if not operation:
                raise HTTPException(status_code=404, detail="Restake operation not found")

            # Change the status of the operation to 'completed'
            operation.status = "completed"
            await session.commit()

            # Record the completed restake in the history
            restake_history = await record_restake_history(session, request.operation_id)

            if restake_history:
                return {"message": "Restake confirmed and history recorded", "history": restake_history}
            else:
                raise HTTPException(status_code=500, detail="Failed to record restake history")

        except Exception as e:
            print(f"Unexpected error: {e}")
            raise HTTPException(status_code=500, detail="An unexpected error occurred")