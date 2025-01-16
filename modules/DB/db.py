from sqlalchemy import (create_engine, Column, Integer, String, Float, Date, ForeignKey)
from sqlalchemy.orm import relationship, sessionmaker, declarative_base

Base = declarative_base()


class City(Base):
    __tablename__ = 'cities'

    id = Column(Integer, primary_key=True, autoincrement=True)
    city = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    users = relationship("User", back_populates='city', cascade='all, delete')
    weathers = relationship("Weather", back_populates='city', cascade='all, delete')


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    city_id = Column(Integer, ForeignKey('cities.id', ondelete='SET NULL'))

    city = relationship("City", back_populates='users')


class Weather(Base):
    __tablename__ = 'weather'

    id = Column(Integer, primary_key=True, autoincrement=True)
    city_id = Column(Integer, ForeignKey('cities.id', ondelete='CASCADE'), nullable=False)
    temperature = Column(Float, nullable=False)
    wind_speed = Column(Float, nullable=False)
    humidity = Column(Integer, nullable=False)
    precipitation = Column(Float)
    time = Column(Date, nullable=False)

    city = relationship("City", back_populates='weathers')
