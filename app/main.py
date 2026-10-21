from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from app.models.database import Base, engine
from app.models import entities
from app.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="FleetOps API",
    version="1.0.0",
    lifespan=lifespan,
)


app.include_router(router)


@app.get("/")
def root():
    return {
        "application": "FleetOps",
        "status": "running"
    }


@app.get("/health")
def health():
    return {
        "status": "UP"
    }

@app.get("/addition")
def addition(a: int, b: int):
	return a + b

@app.get("/division")
def division(a: int, b: int):
	return a / b


@app.get("/health/db")
def health_db():
	try:
		with engine.connect() as connection:
		     connection.execute(text("SELECT 1"))
		
		return {
		    	"status": "UP",
			"database": "UP"
		}
	
	except Exception as error:
		return {
			"status": "DOWN",
			"database": "DOWN",
			"error": str(error)
                }
