from datetime import datetime, timedelta
import asyncio
import httpx
from fastapi import FastAPI, HTTPException, Query
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, selectinload
from sqlalchemy import select
from modules.DB.db import City, Base, User, Weather
from dotenv import load_dotenv
import os
from pydantic import BaseModel

load_dotenv()
# Получаем URL для подключения к базе данных
DATABASE_URL = os.getenv("DATEBASE_URL")

# URL для получения данных о погоде
URL_WHEATHER = "https://api.open-meteo.com/v1/forecast"

# Время обновления погодных данных (в секундах)
TIME = 15 * 60

if not DATABASE_URL:
    raise ValueError("DATABASE_URL не определена в .env ")

app = FastAPI()

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# Модели данных для создания города, параметров погоды и пользователя
class CityCreate(BaseModel):
    city: str
    latitude: float
    longitude: float


class WeatherParameters(BaseModel):
    temperature: bool = True
    wind_speed: bool = True
    pressure: bool = True
    humidity: bool = False
    precipitation: bool = False


class UserCreate(BaseModel):
    name: str


# Переменная для хранения данных о погоде
weather_data = {}


# Событие при старте приложения, создается база данных и запускается задача для обновления данных о погоде
@app.on_event('startup')
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    asyncio.create_task(update_weather_data())


# Событие при завершении работы приложения, очищает соединение с базой данных
@app.on_event('shutdown')
async def shutdown():
    await engine.dispose()


# Создание нового пользователя
@app.post('/users/')
async def create_user(user: UserCreate):
    async with async_session() as session:
        new_user = User(name=user.name)
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return {"id": 1, "name": user.name}


# Получение списка всех пользователей
@app.get("/all_users/")
async def get_all_users():
    async with async_session() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        return [{"id": user.id, "name": user.name} for user in users]


# Получение списка всех городов
@app.get('/all_cities/')
async def get_all_cities():
    async with async_session() as session:
        result = await session.execute(select(City))
        cities = result.scalars().all()
        return [{"id": city.id, 'name': city.city, "latitude": city.latitude, 'longitude': city.longitude} for city in
                cities]


# Получение городов, привязанных к определенному пользователю
@app.get('/cities/')
async def get_all_user_cities(user_id: int):
    async with async_session() as session:
        result = await session.execute(select(City).where(City.users.any(User.id == user_id)))
        cities = result.scalars().all()
        return [{"id": city.id, 'name': city.city, "latitude": city.latitude, 'longitude': city.longitude} for city in
                cities]


# Добавление нового города для пользователя
@app.post('/cities/')
async def add_city(user_id: int, city: CityCreate):
    async with async_session() as session:
        user = await session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        new_city = City(city=city.city, latitude=city.latitude, longitude=city.longitude)
        session.add(new_city)
        user.city = new_city
        await session.commit()
        await session.refresh(new_city)
        return {"id": new_city.id, "name": new_city.city, "latitude": new_city.latitude,
                "longitude": new_city.longitude}


# Получение данных о текущей погоде для города
@app.get('/weather/')
async def get_weather(latitude: float, longitude: float):
    async with httpx.AsyncClient() as client:
        response = await client.get(URL_WHEATHER, params={
            "latitude": latitude,
            "longitude": longitude,
            "current_weather": True,
            "hourly": "pressure_msl"
        })
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Ошибка при запросе к Open-Meteo API")
    data = response.json().get('current_weather')
    hourly_pressure = response.json().get("hourly", {}).get('pressure_msl')
    pressure = hourly_pressure[0] if hourly_pressure else None
    if not data:
        raise HTTPException(status_code=404, detail="Данные о погоде не найдены")
    return {
        "temperature": data.get("temperature"),
        "wind_speed": data.get("windspeed"),
        "pressure": pressure
    }


# Получение прогноза погоды для города
@app.get('/forecast/')
async def get_city_forecast(user_id: int, city: str, time: datetime, params: WeatherParameters):
    async with async_session() as session:
        result = await session.execute(
            select(City)
            .options(selectinload(City.weathers))
            .where(City.city == city, City.users.any(User.id == user_id))
        )
        city_data = result.scalars().first()
        if not city_data or not city_data.weathers:
            raise HTTPException(status_code=404, detail="Прогноз для указанного города отсутствует")

        forecast = min(
            city_data.weathers,
            key=lambda w: abs(datetime.combine(w.time, datetime.min.time()) - time),
            default=None
        )
        if not forecast:
            raise HTTPException(status_code=404, detail="Данные о погоде не найдены на ближайшее время")

        response = {}
        if params.temperature:
            response["temperature"] = forecast.temperature
        if params.wind_speed:
            response["wind_speed"] = forecast.wind_speed
        if params.humidity:
            response["humidity"] = forecast.humidity
        if params.precipitation:
            response["precipitation"] = forecast.precipitation

        return response


# Асинхронная функция для обновления данных о погоде каждые 15 минут
async def update_weather_data():
    while True:
        try:
            async with async_session() as session:
                result = await session.execute(select(City))
                cities = result.scalars().all()

            async with httpx.AsyncClient() as client:
                for city in cities:
                    res = await client.get(URL_WHEATHER, params={
                        "latitude": city.latitude,
                        "longitude": city.longitude,
                        "hourly": "temperature_2m,windspeed_10m,pressure_msl,relative_humidity_2m,precipitation",
                        "start": datetime.now().strftime("%Y-%m-%dT00:00"),
                        "end": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%dT00:00")
                    })
                    if res.status_code == 200:
                        for hour, temperature in enumerate(res.json()["hourly"]["temperature_2m"]):
                            weather_entry = Weather(
                                city_id=city.id,
                                temperature=temperature,
                                wind_speed=res.json()["hourly"]["windspeed_10m"][hour],
                                humidity=res.json()["hourly"]["relative_humidity_2m"][hour],
                                precipitation=res.json()["hourly"]["precipitation"][hour],
                                time=datetime.now() + timedelta(hours=hour)
                            )
                            session.add(weather_entry)
                        await session.commit()
        except Exception as e:
            print(f"Error updating weather data: {e}")

        await asyncio.sleep(TIME)
