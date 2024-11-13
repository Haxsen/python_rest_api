from sqlalchemy.ext.asyncio import AsyncSession
from app.models import RestakeHistory, RestakeOperation
from datetime import datetime

async def record_restake_history(session: AsyncSession, operation_id: int):
    # Fetch the restake operation from the database
    operation = await session.get(RestakeOperation, operation_id)
    if operation and operation.status == "completed":
        # Create a new RestakeHistory entry
        restake_history = RestakeHistory(
            restake_operation_id=operation.id,
            amount=operation.amount,
            status=operation.status,
            completed_at=datetime.utcnow()
        )
        session.add(restake_history)
        await session.commit()  # Commit the changes

        return restake_history  # Return the recorded history
    return None  # Return None if the operation is not found or isn't completed
