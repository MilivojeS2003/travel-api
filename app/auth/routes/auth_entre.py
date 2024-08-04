from datetime import timedelta, datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status
from database import SessionLocal
from ..models.model_auth import Business,Entrepreneur
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError

router = APIRouter(
    prefix='/auth_entre',
    tags=['auth_entre']
)

SECRET_KEY = '197b2c37c391bed93fe80344fe73b806947a65e36206e05a1a23c2fa12702fe3'
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='/auth_entre/token')

class EntrepreneursRequest(BaseModel):
    name: str
    email: str
    password: str
    description: str
    business: str
    destination: str

class Token(BaseModel):
    access_token: str
    token_type: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

def authenticate_entre(name: str, password: str, db: Session):
    entre = db.query(Entrepreneur).filter(Entrepreneur.name == name).first()
    if not entre:
        return False
    if not bcrypt_context.verify(password, entre.hashed_password):
        return False
    return entre

def create_access_token_entre(name: str, user_id: int, expires_delta: timedelta):
    encode = {'sub': name, 'id': user_id}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

def find_business_id(name: str, db: Session):
    business = db.query(Business).filter(Business.name == name).first()
    if business:
        return business.id
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business not found")

# ----------------------------- Entrepreneurs --------------------------------------------

@router.post("/")
async def create_entre(create_entr_request: EntrepreneursRequest, db: db_dependency):

    create_entr_model = Entrepreneur(
        name=create_entr_request.name,
        email=create_entr_request.email,
        hashed_password=bcrypt_context.hash(create_entr_request.password),
        destination=create_entr_request.destination,
        business_id = find_business_id(create_entr_request.business, db),
        description=create_entr_request.description
    )
    db.add(create_entr_model)
    db.commit()
    return {"message": "Entrepreneur created successfully"}

@router.post("/token", response_model=Token)
async def login_for_access_token_entre(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    entre = authenticate_entre(form_data.username, form_data.password, db)
    if not entre:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate entrepreneur.')
    token = create_access_token_entre(entre.name, entre.id, timedelta(minutes=20))
    return {'access_token': token, 'token_type': 'bearer'}

async def get_current_entre(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        name: str = payload.get('sub')
        entre_id: int = payload.get('id')
        if name is None or entre_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')
        return {'username': name, 'id': entre_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')
