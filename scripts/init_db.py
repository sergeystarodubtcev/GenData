"""
Скрипт для инициализации базы данных и создания первого администратора
"""
import sys
import os

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models import User
from app.auth import get_password_hash
from app.config import settings


def init_db():
    """Создание таблиц и первого администратора"""
    # Создаем все таблицы
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    try:
        # Проверяем, существует ли уже администратор
        admin = db.query(User).filter(User.login == "admin").first()
        if not admin:
            # Создаем первого администратора
            admin = User(
                login="admin",
                hashed_password=get_password_hash(settings.admin_default_password),
                full_name="Администратор",
                role="admin",
                is_active=True
            )
            db.add(admin)
            db.commit()
            print(f"✓ Создан администратор:")
            print(f"  Логин: admin")
            print(f"  Пароль: {settings.admin_default_password}")
        else:
            print("✓ Администратор уже существует")
    except Exception as e:
        print(f"✗ Ошибка при создании администратора: {e}")
        db.rollback()
    finally:
        db.close()
    
    print("✓ База данных инициализирована")


if __name__ == "__main__":
    init_db()

