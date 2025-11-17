# Примеры использования API GenData

## Получение токена

```bash
curl -X POST "http://localhost:8000/auth/token" \
  -H "Content-Type: application/json" \
  -d '{
    "login": "admin",
    "password": "admin123"
  }'
```

**Ответ:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

## Создание пользователя

```bash
curl -X POST "http://localhost:8000/admin/users" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "login": "newuser",
    "password": "password123",
    "full_name": "Новый Пользователь",
    "company_name": "ООО Компания",
    "role": "client"
  }'
```

## Получение списка пользователей

```bash
curl -X GET "http://localhost:8000/admin/users?skip=0&limit=100" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Получение пользователя по ID

```bash
curl -X GET "http://localhost:8000/admin/users/1" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Обновление пользователя

```bash
curl -X PUT "http://localhost:8000/admin/users/1" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Обновленное Имя",
    "role": "employee"
  }'
```

## Удаление пользователя

```bash
curl -X DELETE "http://localhost:8000/admin/users/1" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Импорт пользователей из CSV

```bash
curl -X POST "http://localhost:8000/admin/users/import" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -F "file=@examples/users_example.csv"
```

## Импорт пользователей из XLSX

```bash
curl -X POST "http://localhost:8000/admin/users/import" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -F "file=@users.xlsx"
```

## Пример использования в Python

```python
import requests

BASE_URL = "http://localhost:8000"

# Получение токена
response = requests.post(
    f"{BASE_URL}/auth/token",
    json={"login": "admin", "password": "admin123"}
)
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Создание пользователя
user_data = {
    "login": "testuser",
    "password": "testpass123",
    "full_name": "Тестовый Пользователь",
    "company_name": "Тестовая Компания",
    "role": "client"
}
response = requests.post(
    f"{BASE_URL}/admin/users",
    json=user_data,
    headers=headers
)
print(response.json())

# Получение списка пользователей
response = requests.get(
    f"{BASE_URL}/admin/users",
    headers=headers
)
users = response.json()
print(f"Всего пользователей: {len(users)}")

# Импорт из CSV
with open("examples/users_example.csv", "rb") as f:
    files = {"file": f}
    response = requests.post(
        f"{BASE_URL}/admin/users/import",
        files=files,
        headers=headers
    )
    print(response.json())
```

## Пример использования в JavaScript (fetch)

```javascript
const BASE_URL = "http://localhost:8000";

// Получение токена
async function getToken(login, password) {
  const response = await fetch(`${BASE_URL}/auth/token`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ login, password }),
  });
  const data = await response.json();
  return data.access_token;
}

// Создание пользователя
async function createUser(token, userData) {
  const response = await fetch(`${BASE_URL}/admin/users`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(userData),
  });
  return await response.json();
}

// Использование
(async () => {
  const token = await getToken("admin", "admin123");
  const user = await createUser(token, {
    login: "jsuser",
    password: "password123",
    full_name: "JS Пользователь",
    role: "client",
  });
  console.log(user);
})();
```

