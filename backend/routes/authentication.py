# In routes/authentication.py
from fastapi import Depends,APIRouter, HTTPException, status
from typing import Optional
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
from models.auth import SendOtpRequest, Token, VerifyOtpRequest
from models.users import User, UserSignUp, UserOut
import random
load_dotenv()

otp_storage = {} #new addition
SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="verify-otp-and-login")
#=======================================Helper Functions===================================

auth_router = APIRouter()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def verify_otp(request_body: VerifyOtpRequest):
    """
    Verifies the OTP code provided by the user against the one in otp_storage.
    """
    stored_otp = otp_storage.get(request_body.phone_number)

    if not stored_otp:
        raise HTTPException(status_code=404, detail="OTP not found. Please request a new one.")

    if stored_otp == request_body.otp_code:
        # OTP is correct, remove it to prevent reuse
        del otp_storage[request_body.phone_number]
        return {"success": True, "message": "Verification successful"}
    else:
        raise HTTPException(status_code=400, detail="Invalid OTP code")


async def send_otp_sms(phone_number: str):
    """
    Generates a random OTP, stores it, and prints it to the terminal.
    """
    # Generate a 6-digit OTP
    otp_code = str(random.randint(100000, 999999))
    
    # Store the OTP with the phone number as the key
    otp_storage[phone_number] = otp_code
    
    # Print the OTP to the console for the developer to see
    print("----------------------------------------------------")
    print(f"✅ OTP for phone number {phone_number} is: {otp_code}")
    print("----------------------------------------------------")
    
    return {"status": "sent", "message": f"OTP generated and printed to terminal for {phone_number}"}




@auth_router.post("/send-login-otp")
async def send_otp(request_body: SendOtpRequest):
    """
    Endpoint to send an OTP to a user's phone number.
    Expects JSON body: {"phone_number": "+919876543210"}
    """
    
    # --- THIS IS THE FIX (Removed 'User.role' check) ---
    if await User.find_one(User.phone_number == request_body.phone_number):
       return await send_otp_sms(request_body.phone_number)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No account is associated with this phone number."
        )


#=======================================API ENDPOINTS=======================================
@auth_router.post("/signUp", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def sign_up(user_in: UserSignUp):
    if await User.find_one(User.user_name == user_in.user_name):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Username is already taken")
    if await User.find_one(User.phone_number == user_in.phone_number):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Phone number is already registered")
    
    # --- THIS IS THE FIX (Changed 'email_id' to 'email') ---
    user = User(
        user_name=user_in.user_name, 
        phone_number=user_in.phone_number, 
        email=user_in.email,  # <-- FIX
        full_name=user_in.full_name
    )
    
    await user.insert()

    return user


@auth_router.post("/verify-otp-and-login", response_model=Token)
async def verify_otp_and_login(request: VerifyOtpRequest):
    """
    Verifies the OTP and, if successful, returns a JWT access token.
    """
    verification_result = await verify_otp(request)
    
    if not verification_result.get("success"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP verification failed.")

    user = await User.find_one(User.phone_number == request.phone_number)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found after OTP verification.")
    
    # Create the Access Token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.uuid)}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_uuid: str = payload.get("sub")
        if user_uuid is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Fetch user by UUID from the database
    user = await User.find_one(User.uuid == user_uuid) # Assuming your User model has 'uuid'
    if user is None:
        raise credentials_exception
    return user

# --- NEW ENDPOINT ---
@auth_router.get("/users/me", response_model=UserOut)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Get the details of the currently authenticated user.
    """
    # UserOut model should automatically handle the response structure
    return current_user