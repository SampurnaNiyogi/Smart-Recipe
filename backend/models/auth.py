from pydantic import BaseModel, Field
from typing import Optional, Literal

class SendOtpRequest(BaseModel):
    phone_number: str = Field(..., example="+919876543210")
    

class VerifyOtpRequest(BaseModel):
    phone_number: str = Field(..., example="+919876543210")
    otp_code: str = Field(..., example="123456", min_length=4, max_length=7)
    

class Token(BaseModel):
    access_token: str
    token_type: str