import httpx
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

import models
import schemas
import auth
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

POKEAPI_BASE_URL = "https://pokeapi.co/api/v2"

@app.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if len(user.password) < 8:
        raise HTTPException(status_code=400, detail="La contraseña debe tener al menos 8 caracteres")
    
    if not user.username.strip() or not user.last_name.strip() or not user.email.strip():
        raise HTTPException(status_code=400, detail="Todos los campos son requeridos")

    db_user = auth.get_user(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="El nombre de usuario ya está registrado")
    
    db_email = db.query(models.User).filter(models.User.email == user.email).first()
    if db_email:
        raise HTTPException(status_code=400, detail="El correo electrónico ya está registrado")

    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        last_name=user.last_name,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth.get_user(db, form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/pokemon/{name}")
async def get_pokemon(name: str):
    name = name.lower().replace(" ", "-")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{POKEAPI_BASE_URL}/pokemon/{name}")
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Pokemon not found")
        return response.json()

@app.get("/api/pokemon")
async def list_pokemon(offset: int = 0, limit: int = 20):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{POKEAPI_BASE_URL}/pokemon?offset={offset}&limit={limit}")
        return response.json()

@app.get("/api/type/{type_name}")
async def get_type(type_name: str):
    type_name = type_name.lower().replace(" ", "-")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{POKEAPI_BASE_URL}/type/{type_name}")
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Type not found")
        return response.json()

@app.get("/api/move/{name}")
async def get_move(name: str):
    name = name.lower().replace(" ", "-")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{POKEAPI_BASE_URL}/move/{name}")
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Move not found")
        return response.json()

@app.get("/api/pokemon-species/{name}")
async def get_pokemon_species(name: str):
    name = name.lower().replace(" ", "-")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{POKEAPI_BASE_URL}/pokemon-species/{name}")
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Species not found")
        return response.json()

@app.get("/api/evolution-chain/{id}")
async def get_evolution_chain(id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{POKEAPI_BASE_URL}/evolution-chain/{id}")
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Evolution chain not found")
        return response.json()

@app.get("/api/favorites", response_model=list[schemas.Favorite])
def get_favorites(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    favorites = db.query(models.Favorite).filter(models.Favorite.owner_id == current_user.id).all()
    return favorites

@app.post("/api/favorites", response_model=schemas.Favorite)
def add_favorite(favorite: schemas.FavoriteCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    db_favorite = db.query(models.Favorite).filter(
        models.Favorite.owner_id == current_user.id,
        models.Favorite.pokemon_name == favorite.pokemon_name
    ).first()
    if db_favorite:
        raise HTTPException(status_code=400, detail="Already in favorites")
    
    new_fav = models.Favorite(**favorite.dict(), owner_id=current_user.id)
    db.add(new_fav)
    db.commit()
    db.refresh(new_fav)
    return new_fav

@app.delete("/api/favorites/{pokemon_name}")
def delete_favorite(pokemon_name: str, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    db_favorite = db.query(models.Favorite).filter(
        models.Favorite.owner_id == current_user.id,
        models.Favorite.pokemon_name == pokemon_name
    ).first()
    if not db_favorite:
        raise HTTPException(status_code=404, detail="Favorite not found")
    
    db.delete(db_favorite)
    db.commit()
    return {"message": "Deleted"}
