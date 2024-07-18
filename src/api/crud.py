from typing import List, Dict

from aiosmtplib import SMTPRecipientsRefused, SMTPDataError
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from starlette import status
from starlette.responses import JSONResponse

from src.database.models import User
from src.dependencies import get_user_service, get_current_user
from src.schemas.schemas import ShowUserSchema, UserCreationSchema, UpdateUserSchema, ChangePasswordSchema, EmailSchema
from src.services.service import UserService

user_router: APIRouter = APIRouter(prefix="/user", tags=["user", ])


@user_router.post(path="/", response_model=ShowUserSchema)
async def create_user(
        body: UserCreationSchema,
        service: UserService = Depends(get_user_service)
) -> JSONResponse:
    """
    Эндпоинт, отвечающий за создание (регистрацию) пользователя

    В случае, если пользователь с такими username или email уже
    существует, возвращается исключение с кодом 409

    В случае, если не удалось отправить письмо для подтверждения регистрации,
    возвращается исключение с кодом 422

    В случае успешной работы на указанную при регистрации почту отправляется
    письмо с токеном, который необходимо использовать в эндпоинте
    verify_email для верификации созданного в базе данных пользователя
    """

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
    except (IntegrityError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this credentials already exists",
        )
    except (SMTPRecipientsRefused, SMTPDataError):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Cannot send email"
        )


@user_router.get(path="/", response_model=List[ShowUserSchema])
async def get_users(
        service: UserService = Depends(get_user_service)
) -> List[User]:
    """
    Эндпоинт, отвечающий за получение списка всех
    верифицированных пользователей
    """

    users: List[User] = await service.get_users()
    return users


@user_router.delete(path="/")
async def delete_user(
        user: User = Depends(get_current_user),
        service: UserService = Depends(get_user_service)
) -> JSONResponse:
    """
    Эндпоинт, отвечающий за удаление аккаунта пользователя

    Данные о том, какого пользователя необходимо удалить берутся
    из заголовка запроса (то есть удаление возможно лишь авторизованным
    пользователем, причем именно своего аккаунта)

    В случае успешной работы возвращается сообщение об удалении пользователя
    """

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
    """
    Эндпоинт, отвечающий за обновление информации о пользователе
    (за исключением пароля и электронной почты)

    На вход должен поступить как минимум один параметр для изменения
    из name, surname, username. Данные о пользователе,
    которого необходимо изменить, берутся из
    запроса (то есть обновление данных возможно лишь авторизованным
    пользователем, причем именно своего аккаунта)

    В случае, если пользователь с таким username уже существует,
    возвращается исключение с кодом 409

    В случае, если не было передано ни одного параметра, то возвращается
    исключение с кодом 400

    В случае успешной работы возвращаются обновленные данные
    пользователя
    """

    parameters_for_update: Dict[str, str] = body.model_dump(
        exclude_none=True
    )
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
    """
    Эндпоинт, отвечающий за изменение пароля пользователя

    На вход поступает старый пароль, новый пароль и его подтверждение.
    Данные о пользователе, которого необходимо изменить, берутся из
    запроса (то есть обновление пароля возможно лишь авторизованным
    пользователем, причем именно своего аккаунта)

    В случае, если старый пароль неверен, то возникает исключение с
    кодом 400

    В случае успешной работы возвращаются данные обновленного
    пользователя
    """

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
    """
    Эндпоинт, отвечающий за смену адреса электронной почты

    На вход поступает новый адрес электронной почты. Данные о том,
    почта какого пользователя должна быть обновлена берутся
    из заголовка запроса (то есть смена почты возможно лишь авторизованным
    пользователем, причем именно своего аккаунта)

    В случае, если пользователь уже использует этот адрес электронной
    почты, возникает исключение с кодом 409

    Если письмо для подтверждения смены адреса электронной почты отправить
    не удалось, возникает исключение с кодом 422

    В случае успешной работы пользователю на указанную почту
    отправляется письмо с токеном, которой необходимо использовать
    в эндпоинте confirm_email_change, а в рамках ответа возвращается
    сообщение об успешной отправке
    """

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
