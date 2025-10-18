from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException
from starlette.responses import JSONResponse
from utils.i18n import translate_detail
from fastapi.middleware.cors import CORSMiddleware
from routers import patientRouter, reservationRouter, authRouter, hospitalRouter
from dotenv import load_dotenv
import importlib
import db.database # Import db.database first
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Force reload db.database to ensure latest changes are picked up
importlib.reload(db.database)

app = FastAPI()

# CORS 설정
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 포함
app.include_router(authRouter.router)
app.include_router(patientRouter.router)
app.include_router(reservationRouter.router)
app.include_router(hospitalRouter.router)

@app.get("/")
def read_root():
    return {"message": "Badara Dental Clinic API is running."}


@app.exception_handler(HTTPException)
async def http_exception_to_japanese(request, exc: HTTPException):
    translated = translate_detail(exc.detail)
    return JSONResponse(status_code=exc.status_code, content={"detail": translated}, headers=exc.headers)


@app.exception_handler(RequestValidationError)
async def validation_exception_to_japanese(request, exc: RequestValidationError):
    # 利用者向けに簡潔な日本語メッセージのみを返す
    return JSONResponse(
        status_code=422,
        content={
            "detail": "入力内容に誤りがあります。ご確認ください。",
        },
    )
