from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
import pandas as pd
import io
from app.database import get_db
from app.auth import get_current_admin_user
from app.models import User
from app.schemas import UserCreate, UserResponse, UserUpdate
from app import crud


def convert_user_to_response(user: User) -> UserResponse:
    """Конвертация User модели в UserResponse с маппингом user_metadata -> metadata"""
    return UserResponse(
        id=user.id,
        login=user.login,
        full_name=user.full_name,
        company_name=user.company_name,
        role=user.role,
        metadata=user.user_metadata,
        created_at=user.created_at,
        updated_at=user.updated_at,
        is_active=user.is_active
    )

router = APIRouter(prefix="/admin/users", tags=["users"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Создать нового пользователя"""
    # Проверяем, что пользователь с таким логином не существует
    db_user = crud.get_user_by_login(db, login=user.login)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким логином уже существует"
        )
    created_user = crud.create_user(db=db, user=user)
    return convert_user_to_response(created_user)


@router.get("/", response_model=List[UserResponse])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Получить список пользователей"""
    users = crud.get_users(db, skip=skip, limit=limit)
    return [convert_user_to_response(user) for user in users]


@router.get("/{user_id}", response_model=UserResponse)
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Получить пользователя по ID"""
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    return convert_user_to_response(db_user)


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Обновить пользователя"""
    db_user = crud.update_user(db, user_id=user_id, user_update=user_update)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    return convert_user_to_response(db_user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Удалить пользователя"""
    success = crud.delete_user(db, user_id=user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    return None


@router.post("/import", status_code=status.HTTP_200_OK)
def import_users(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Импорт пользователей из CSV или XLSX файла"""
    
    # Проверяем расширение файла
    if not (file.filename.endswith('.csv') or file.filename.endswith('.xlsx')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Файл должен быть в формате CSV или XLSX"
        )
    
    try:
        # Читаем файл
        contents = file.file.read()
        
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents), encoding='utf-8')
        else:
            df = pd.read_excel(io.BytesIO(contents))
        
        # Ожидаемые колонки: login, full_name, company_name, role
        required_columns = ['login']
        if not all(col in df.columns for col in required_columns):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Файл должен содержать колонки: {', '.join(required_columns)}"
            )
        
        imported_count = 0
        updated_count = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                login = str(row['login']).strip()
                if not login:
                    errors.append(f"Строка {index + 2}: пустой логин")
                    continue
                
                full_name = str(row.get('full_name', '')).strip() if pd.notna(row.get('full_name')) else None
                company_name = str(row.get('company_name', '')).strip() if pd.notna(row.get('company_name')) else None
                role = str(row.get('role', 'client')).strip() if pd.notna(row.get('role')) else 'client'
                
                # Валидация роли
                valid_roles = ['client', 'employee', 'investor', 'admin']
                if role not in valid_roles:
                    role = 'client'
                
                # Собираем метаданные из остальных колонок
                metadata = {}
                for col in df.columns:
                    if col not in ['login', 'full_name', 'company_name', 'role']:
                        if pd.notna(row[col]):
                            metadata[col] = str(row[col])
                
                # Проверяем, существует ли пользователь
                existing_user = crud.get_user_by_login(db, login)
                
                if existing_user:
                    crud.create_or_update_user_from_import(
                        db=db,
                        login=login,
                        full_name=full_name,
                        company_name=company_name,
                        role=role,
                        user_metadata=metadata if metadata else None
                    )
                    updated_count += 1
                else:
                    crud.create_or_update_user_from_import(
                        db=db,
                        login=login,
                        full_name=full_name,
                        company_name=company_name,
                        role=role,
                        user_metadata=metadata if metadata else None
                    )
                    imported_count += 1
                    
            except Exception as e:
                errors.append(f"Строка {index + 2}: {str(e)}")
        
        return {
            "message": "Импорт завершен",
            "imported": imported_count,
            "updated": updated_count,
            "errors": errors if errors else None
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка при обработке файла: {str(e)}"
        )

