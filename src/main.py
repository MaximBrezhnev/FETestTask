import uvicorn
from fastapi import FastAPI, APIRouter

from src.api.auth import auth_router
from src.api.verification import verification_router
from src.settings import project_settings
from src.api.crud import user_router

app: FastAPI = FastAPI(title=project_settings.APP_TITLE)

main_router: APIRouter = APIRouter(prefix="/api")
main_router.include_router(user_router)
main_router.include_router(auth_router)
main_router.include_router(verification_router)

app.include_router(main_router)

if __name__ == "__main__":
    uvicorn.run(
        app=app,
        host=project_settings.APP_HOST,
        port=project_settings.APP_PORT
    )
