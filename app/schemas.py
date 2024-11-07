from pydantic import BaseModel

class RestakeRequest(BaseModel):
    user_id: int
    amount: float

class ConfirmRequest(BaseModel):
    operation_id: int