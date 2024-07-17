import uvicorn
from fastapi import FastAPI

from src.settings import project_settings
from src.user.routes import user_router

app: FastAPI = FastAPI(title=project_settings.APP_TITLE)

app.include_router(user_router)

if __name__ == "__main__":
    uvicorn.run(
        app=app,
        host=project_settings.APP_HOST,
        port=project_settings.APP_PORT
    )
