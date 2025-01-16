# Прогноз погоды и управление пользователями

Этот проект представляет собой API для работы с погодными данными и управления пользователями и городами. API позволяет добавлять пользователей и города, а также получать данные о погоде для определенных городов.

Вы можете установить все необходимые зависимости, используя файл `requirements.txt`, если он есть, с помощью команды:
pip install -r requirements.txt


Запуск
1) Запустите сервер FastAPI с помощью команды:
python script.py
2) После этого сервер будет доступен по адресу http://127.0.0.1:8000.

# API Документация

## 1. Создание пользователя
**POST** `http://localhost:8000/users/`

Создает нового пользователя.

**Headers:**

Content-Type application/json

**Тело запроса:**
```json
{
  "name": "John Doe"
}
```
Ответ: 
``` json{
  "id": 1,
  "name": "Имя пользователя"
}
```
2. Получение всех пользователей
GET http://localhost:8000/all_users/

Возвращает список всех пользователей.

Ответ:
``` json
[
  {
    "id": 1,
    "name": "John Doe"
  },
  {
    "id": 2,
    "name": "Jane Doe"
  }
]
```
3. Добавление города для пользователя
POST http://localhost:8000/cities/

Добавляет новый город для пользователя.

Параметры запроса:

user_id — ID пользователя, для которого добавляется город.

**Тело запроса:**
```json
{
  "city": "Moscow",
  "latitude": 55.7558,
  "longitude": 37.6176
}
```

**Ответ**
```json
{
  "id": 1,
  "name": "Moscow",
  "latitude": 55.7558,
  "longitude": 37.6176
}

```
4. Получение погоды для города
GET http://localhost:8000/weather/

Получение текущих погодных данных для города.

**Параметры запроса:**

latitude — широта города.
longitude — долгота города.

**Пример запроса:**

GET http://localhost:8000/weather/?latitude=55.7558&longitude=37.6176

**Ответ**
```json
{
  "temperature": 5.2,
  "wind_speed": 3.5,
  "pressure": 1013
}
```
5. Прогноз погоды для города
GET http://localhost:8000/forecast/

Получение прогноза погоды для города на основе данных в базе.

**Параметры запроса:**

user_id — ID пользователя.

city — название города.

time — время, для которого требуется прогноз.

**Пример запроса:**

GET http://localhost:8000/forecast/?user_id=1&city=Moscow&time=2025-01-16T14:00:00

**Тело запроса (параметры прогноза погоды):**
```json
{
  "temperature": true,
  "wind_speed": true,
  "humidity": false,
  "precipitation": false
}

```
**Ответ**
```json
{
  "temperature": 6.1,
  "wind_speed": 4.5,
  "precipitation": 1014
}
```
6. Получение всех городов


GET http://localhost:8000/all_cities/

Получение списка всех городов.
**Ответ**
```json
[
  {
    "id": 1,
    "name": "Moscow",
    "latitude": 55.7558,
    "longitude": 37.6176
  },
  {
    "id": 2,
    "name": "London",
    "latitude": 59.9343,
    "longitude": 30.3351
  }
]

```
7. Прогноз погоды для города

GET http://localhost:8000/cities/

Получение списка городов для определенного пользователя.

**Параметры запроса:**

user_id — ID пользователя.

**Пример запроса:**

GET http://localhost:8000/cities/?user_id=1

**Ответ**
```json
[
  {
    "id": 1,
    "name": "Moscow",
    "latitude": 55.7558,
    "longitude": 37.6176
  }
]

```
