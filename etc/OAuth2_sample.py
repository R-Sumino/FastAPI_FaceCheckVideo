from datetime import datetime, timedelta
from typing import Union

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    }
}


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None


class User(BaseModel):
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None


class UserInDB(User):
    hashed_password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
print("1 : pwd_context: ", vars(pwd_context))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
print("2 : oauth2_scheme: ", vars(oauth2_scheme))

app = FastAPI()


def verify_password(plain_password, hashed_password):
    print("3 : plain_password: ", plain_password)
    print("4 : hashed_password: ", hashed_password)
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    print("5 : password: ", password)
    return pwd_context.hash(password)


def get_user(db, username: str):
    print("6 : db: ", db)
    print("7 : username: ", username)
    if username in db:
        user_dict = db[username]
        print("8 : user_dict: ", user_dict)
        return UserInDB(**user_dict)


def authenticate_user(fake_db, username: str, password: str):
    print("9 : fake_db: ", fake_db)
    print("10 : username: ", username)
    print("11 : password: ", password)
    user = get_user(fake_db, username)
    print("12 : user: ", user)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    print("13 : data: ", data)
    print("14 : expires_delta: ", expires_delta)
    to_encode = data.copy()
    print("15 : to_encode: ", to_encode)
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
        print("16 : expire: ", expire)
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
        print("17 : expire: ", expire)
    to_encode.update({"exp": expire})
    print("18 : to_encode after: ", to_encode)
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    print("19 : encoded_jwt: ", encoded_jwt)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    print("20 : token: ", token)
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print("21 : payload: ", payload)
        username: str = payload.get("sub")
        data: timedelta = payload.get("exp")
        print("22 : username: ", username)
        print("32 : data: ", data)
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
        print("23 : token_data: ", token_data)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    print("24 : user: ", user)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    print("25 : current_user: ", current_user)
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    print("26 : form_data: ", vars(form_data))
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    print("27 : user: ", user)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    print("28 : access_token_expires: ", access_token_expires)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    print("29 : access_token: ", access_token)
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    print("30 : current_user: ", current_user)
    return current_user


@app.get("/users/me/items/")
async def read_own_items(current_user: User = Depends(get_current_active_user)):
    print("31 : current_user: ", current_user)
    return [{"item_id": "Foo", "owner": current_user.username}]
