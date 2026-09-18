from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from database import get_session
from models import User
from security import (
    hash_password,
    get_current_user,
    require_admin
)
from schemas import (
    UserCreate,
    UserResponse,
    UserUpdate,
    UserUpdateFull
)


router = APIRouter(
    tags=["Users"]
)


@router.post("/create-user", response_model=UserResponse)
def create_user(
    user_data: UserCreate,
    session: Session = Depends(get_session)
):
    existing_user = session.exec(
        select(User).where(
            User.username == user_data.username
        )
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    user = User(
        username=user_data.username,
        email=user_data.email,
        password=hash_password(user_data.password),
        role=user_data.role
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    return user

@router.get("/users/me", response_model=UserResponse)
def get_me(
    current_user: User = Depends(get_current_user)
):
    return current_user

@router.patch(
    "/admin/users/{user_id}",
    response_model=UserResponse
)
def patch_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session)
):
    user = session.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if user_data.username is not None:
        user.username = user_data.username

    if user_data.email is not None:
        user.email = user_data.email

    if user_data.role is not None:
        user.role = user_data.role

    session.add(user)
    session.commit()
    session.refresh(user)

    return user

@router.put(
    "/admin/users/{user_id}",
    response_model=UserResponse
)
def update_user(
    user_id: int,
    user_data: UserUpdateFull,
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session)
):
    user = session.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    user.username = user_data.username
    user.email = user_data.email
    user.role = user_data.role

    session.add(user)
    session.commit()
    session.refresh(user)

    return user


@router.delete("/admin/users/{user_id}")
def delete_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session)
):
    user = session.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    session.delete(user)
    session.commit()

    return {
        "message": "User deleted successfully"
    }
