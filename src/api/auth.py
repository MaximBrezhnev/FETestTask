from typing import Dict

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from src.database.models import User
from src.schemas.schemas import TokenSchema
from src.dependencies import get_user_service, get_current_user
from src.services.service import UserService

auth_router: APIRouter = APIRouter(
    prefix="/auth",
    tags=["auth", ]
)


@auth_router.post(path="/login", response_model=TokenSchema)
async def login(
    body: OAuth2PasswordRequestForm = Depends(),
    service: UserService = Depends(get_user_service),
) -> TokenSchema:
    """
    Эндпоинт, отвечающий за вход пользователя в систему на
    основании предоставленных username и password. Остальные
    данные во встроенной схеме OAuth2PasswordRequestForm необязательны
    для заполнения

    Если пользователя с таким username не существует или
    пароль неверен, то возвращается исключение

    Если вход произошел успешно, то эндпоинт возвращает
    access token, который имеет короткий срок службы и должен
    присылаться в заголовках вместе с каждым запросом
    (Authorization: Bearer <access token>)

    Также возвращает refresh token для обновления
    access token'а через эндпоинт refresh_token
    """

    try:
        token_data: Dict[str, str] = await service.login(
            username=body.username,
            password=body.password
        )
        return TokenSchema(**token_data)

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )


@auth_router.post(path="/refresh-token", response_model=TokenSchema)
async def refresh_token(
    user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> TokenSchema:
    """
    Эндпоинт, который на основании refresh token'а, полученного
    из эндпоинта login возвращает новый access token. Данные
    о текущем пользователя берутся из заголовка запроса
    (Authorization: Bearer <refresh token>)
    """

    token_data: Dict[str, str] = service.refresh_token(user=user)

    return TokenSchema(**token_data)
