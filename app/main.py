from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, users
from app.database import engine
from app.models import Base

# Создаем таблицы (в продакшене используйте Alembic)
# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="GenData API",
    description="Веб-платформа для создания опросов и сбора обратной связи",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене укажите конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(auth.router)
app.include_router(users.router)


@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "message": "GenData API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Проверка здоровья API"""
    return {"status": "ok"}

