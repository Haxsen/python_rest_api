from pydantic import BaseModel

class RestakeRequest(BaseModel):
    user_id: int
    amount: float

class ConfirmRequest(BaseModel):
    operation_id: int

class RegisterUser(BaseModel):
    userid: str
    email: str
    userprivatekey: str

class DepositOrWithdrawRequestRust(BaseModel):
    userid: str
    amount: int

class CheckBalanceRequestRust(BaseModel):
    userid: str