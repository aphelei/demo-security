import os
from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

load_dotenv()

def create_token(id: int, role: str) -> str:
    today = datetime.now(timezone.utc)
    return jwt.encode(payload={
        'iss': 'khunly.be',
        'iat': today.timestamp(),
        'exp': timedelta(minutes=15) + today,
        'role': role,
        'sub': str(id)
    }, key=os.getenv('JWT_SECRET'), algorithm='HS256')

# permet d'extraire le token
oauth2Scheme = OAuth2PasswordBearer(tokenUrl='auth/login', )

# extraire les données (claims) du token
def verify_token(token: Annotated[str, Depends(oauth2Scheme)]) -> dict|None:
    try:
        if os.getenv('TEST_TOKEN', None) and os.getenv('TEST_TOKEN', None) == token:
            return { "role": "admin", "id": 42 }
        return jwt.decode(token, key=os.getenv('JWT_SECRET'), algorithms=['HS256'])
    except jwt.exceptions.DecodeError:
        return None

class RoleGuard:
    def __init__(self, roles: list[str]):
        self.authorized_roles = roles

    # methode appelée par le systeme lors de l'injection
    # pour verifier les droits
    def __call__(self, claims: Annotated[dict, Depends(verify_token)]):
        if not claims or claims['role'] not in self.authorized_roles:
            raise HTTPException(status_code=403)
        return claims