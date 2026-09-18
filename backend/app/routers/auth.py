from app import schemas
from app.core.deps import get_current_user, oauth2_scheme
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from app.database import get_db
from app import crud
from app.core.security import verify_password, create_access_token
from app.models import User, Token

router = APIRouter(tags=["Auth"])


@router.post("/login/")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):

    user = crud.user_crud.get_user_by_username(db, username=form_data.username)

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Identifiants incorrects"
        )

    db.query(Token).filter(
        Token.user_id == user.id, Token.expires_at < datetime.now(timezone.utc)
    ).delete()
    db.commit()

    access_token_expires = timedelta(minutes=30)
    expires_at = datetime.now(timezone.utc) + access_token_expires

    access_token = create_access_token(
        data={"sub": user.username}, expires_at=expires_at
    )

    token_in = schemas.TokenCreate(
        token=access_token, user_id=user.id, expires_at=expires_at
    )

    crud.auth_token_crud.create_token(db, token_in)

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout/")
def logout(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    token: str = Depends(oauth2_scheme),
):

    token_in_db = crud.auth_token_crud.get_token_by_value(db, token_value=token)

    if token_in_db:
        crud.auth_token_crud.delete_token(db, token_id=token_in_db.id)

    return {"detail": "Déconnexion réussie"}
