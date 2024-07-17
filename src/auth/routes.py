from fastapi import APIRouter, Depends, HTTPException
from fastapi import status
from fastapi.security import OAuth2PasswordRequestForm

from src.auth.schemas import TokenSchema
from src.user.dependencies import get_user_service
from src.user.services.services import UserService

auth_router: APIRouter = APIRouter(
    prefix="/auth",
    tags=["auth", ]
)


@auth_router.post(path="/login", response_model=TokenSchema)
async def login(
    body: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(get_user_service),
) -> TokenSchema:
    """Endpoint for user authentication and authorization"""

    try:
        token_data: dict = await user_service.login(
            username=body.username, password=body.password
        )
        return TokenSchema(**token_data)

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
