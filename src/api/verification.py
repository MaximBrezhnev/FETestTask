from fastapi import APIRouter, Depends, HTTPException
from jose import JWTError
from sqlalchemy.exc import IntegrityError
from starlette import status
from starlette.responses import JSONResponse

from src.api.crud import user_router
from src.database.models import User
from src.dependencies import get_user_service
from src.schemas.schemas import ShowUserSchema
from src.services.service import UserService

verification_router: APIRouter = APIRouter(
    prefix="/verification",
    tags=["verification", ]
)


@verification_router.patch(path="/verification", response_model=ShowUserSchema)
async def verify_email(
        token: str,
        service: UserService = Depends(get_user_service)
) -> User:
    """
    Эндпоинт, на основании полученного токена (получаемого на
    электронную почту после регистрации) верифицирующий пользователя
    и возвращающий его данные

    В случае некорректности полученного токена возникает исключение
    с кодом 400
    """
    try:
        user: User = await service.verify_email(token=token)
        return user
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot verify email"
        )


@verification_router.patch(path="/change-email/confirmation")
async def confirm_email_change(
        token: str,
        service: UserService = Depends(get_user_service)
) -> JSONResponse:
    """
    Эндпоинт, отвечающий за подтверждение смены адреса электронной почты

    На вход поступает токен, полученный на электронную почту после использования
    эндпоинта change_email

    В случае некорректности токена возникает исключение с кодом 422

    В случае, если пользователь с такой электронной почтой уже существует - 409

    В случае, если текущий пользователь не был найден - 404

    В случае успешной работы изменяет адрес электронной почты
    пользователя на указанный и возвращает его обновленные данные
    """

    try:
        await service.confirm_email_change(token=token)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Email has been changed successfully"}
        )

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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist"
        )
