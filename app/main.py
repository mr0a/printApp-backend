from fastapi import FastAPI, Depends
from starlette.middleware.authentication import AuthenticationMiddleware
from fastapi.middleware.cors import CORSMiddleware

from app.database import database
from app.core.config import settings
from auth.helpers import JWTAuthenticationBackend, authentication_required

from auth.api.v1 import router as auth_router
from files.api.v1 import router as file_router
from core.api.v1 import router as order_router


app = FastAPI(
        title=settings.PROJECT_NAME,
        description="An API providing end points to use Advanced Data Science models that we have developed",
        version=settings.PROJECT_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    # allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_origins='*',
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(AuthenticationMiddleware, backend=JWTAuthenticationBackend(
    secret_key=settings.SECRET_KEY, prefix="Bearer"
))


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(file_router, prefix="/api/v1/file", tags=["Files"],
                   dependencies=[Depends(authentication_required)])
app.include_router(order_router, prefix="/api/v1/order", tags=["Order"],
                   dependencies=[Depends(authentication_required)])

