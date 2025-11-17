from sqlalchemy.orm import Session
from typing import List, Optional
from app.models import User
from app.schemas import UserCreate, UserUpdate
from app.auth import get_password_hash


def get_user(db: Session, user_id: int) -> Optional[User]:
    """Получить пользователя по ID"""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_login(db: Session, login: str) -> Optional[User]:
    """Получить пользователя по логину"""
    return db.query(User).filter(User.login == login).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Получить список пользователей"""
    return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session, user: UserCreate) -> User:
    """Создать нового пользователя"""
    hashed_password = get_password_hash(user.password)
    db_user = User(
        login=user.login,
        hashed_password=hashed_password,
        full_name=user.full_name,
        company_name=user.company_name,
        role=user.role,
        metadata=user.metadata or {}
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
    """Обновить пользователя"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return None
    
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> bool:
    """Удалить пользователя"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return False
    db.delete(db_user)
    db.commit()
    return True


def create_or_update_user_from_import(
    db: Session,
    login: str,
    full_name: Optional[str] = None,
    company_name: Optional[str] = None,
    role: str = "client",
    metadata: Optional[dict] = None,
    password: Optional[str] = None
) -> User:
    """Создать или обновить пользователя при импорте"""
    db_user = get_user_by_login(db, login)
    
    if db_user:
        # Обновляем существующего пользователя
        if full_name:
            db_user.full_name = full_name
        if company_name:
            db_user.company_name = company_name
        if role:
            db_user.role = role
        if metadata:
            db_user.metadata = {**(db_user.metadata or {}), **metadata}
        db.commit()
        db.refresh(db_user)
        return db_user
    else:
        # Создаем нового пользователя
        # Если пароль не указан, генерируем временный
        if not password:
            import secrets
            password = secrets.token_urlsafe(12)
        
        hashed_password = get_password_hash(password)
        db_user = User(
            login=login,
            hashed_password=hashed_password,
            full_name=full_name,
            company_name=company_name,
            role=role,
            metadata=metadata or {}
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

