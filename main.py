from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import patientRouter, reservationRouter, authRouter
from dotenv import load_dotenv

load_dotenv()

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

@app.get("/")
def read_root():
    return {"message": "Badara Dental Clinic API is running."}