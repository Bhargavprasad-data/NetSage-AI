from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import models
from .database import engine
from .routers import cases, diagnoses, reviews, csv_ops, dashboard

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="NetSage AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cases.router)
app.include_router(diagnoses.router)
app.include_router(reviews.router)
app.include_router(csv_ops.router)
app.include_router(dashboard.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to NetSage AI"}
