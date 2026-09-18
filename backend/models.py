from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String)

    favorites = relationship("Favorite", back_populates="owner")


class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    pokemon_name = Column(String, index=True)
    pokemon_data = Column(String) # JSON string to cache pokemon data
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="favorites")
