from typing import List

from aiosmtplib import SMTPRecipientsRefused, SMTPDataError
from fastapi import APIRouter, Depends
from fastapi import HTTPException
from fastapi import status
from sqlalchemy.exc import IntegrityError
from starlette.responses import JSONResponse
from jose import JWTError

from src.auth.dependencies import get_current_user
from src.user.dependencies import get_user_service
from src.user.models import User
from src.user.schemas import UserCreationSchema, ShowUserSchema, UpdateUserSchema, EmailSchema, ChangePasswordSchema
from src.user.services.services import UserService


user_router: APIRouter = APIRouter(prefix="/user", tags=["user", ])


@user_router.post(path="/", response_model=ShowUserSchema)
async def create_user(
        body: UserCreationSchema,
        service: UserService = Depends(get_user_service)
) -> JSONResponse:
    try:
        await service.create_user(
            name=body.name,
            surname=body.surname,
            username=body.username,
            email=body.email,
            password=body.password1
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Confirmation e-mail was sent"}
        )
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this credentials already exists",
        )
    except (SMTPRecipientsRefused, SMTPDataError):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Cannot send email"
        )


@user_router.patch(path="/verification", response_model=ShowUserSchema)
async def verify_email(
        token: str,
        service: UserService = Depends(get_user_service)
) -> User:
    try:
        user: User = await service.verify_email(token=token)
        return user
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot verify email"
        )


@user_router.get(path="/", response_model=List[ShowUserSchema])
async def get_users(
        service: UserService = Depends(get_user_service)
) -> List[User]:
    users: List[User] = await service.get_users()
    return users


@user_router.delete(path="/")
async def delete_user(
        user: User = Depends(get_current_user),
        service: UserService = Depends(get_user_service)
) -> JSONResponse:
    await service.delete_user(user=user)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "User was deleted successfully"},
    )


@user_router.patch(path="/", response_model=ShowUserSchema)
async def update_user(
        body: UpdateUserSchema,
        user: User = Depends(get_current_user),
        service: UserService = Depends(get_user_service)
) -> User:
    parameters_for_update = body.model_dump(exclude_none=True)
    if not parameters_for_update:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one parameter must be provided"
        )

    try:
        updated_user: User = await service.update_user(
            user=user,
            parameters_for_update=parameters_for_update
        )
        return updated_user

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this username already exists"
        )


@user_router.patch(path="/change-password", response_model=ShowUserSchema)
async def change_password(
    body: ChangePasswordSchema,
    user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> User:
    try:
        updated_user: User = await service.change_password(
            user=user,
            old_password=body.old_password,
            new_password=body.password1
        )
        return updated_user

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect old password was provided",
        )


@user_router.patch(path="/change-email")
async def change_email(
    body: EmailSchema,
    user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
) -> JSONResponse:
    try:
        await user_service.change_email(new_email=body.email, user=user)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Email for email change confirmation was sent"},
        )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The user already uses this email",
        )

    except (SMTPRecipientsRefused, SMTPDataError):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Cannot send email"
        )


@user_router.patch(path="/change-email/confirmation", response_model=ShowUserSchema)
async def confirm_email_change(
    token: str, user_service: UserService = Depends(get_user_service)
) -> User:
    try:
        updated_user: User = await user_service.confirm_email_change(token=token)
        return updated_user

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Could not validate credentials",
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist"
        )


