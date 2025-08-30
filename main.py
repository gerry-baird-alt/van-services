from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import init_db, insert_sample_data
from routes import vehicles, bookings, admin, branches, availability


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    insert_sample_data()
    yield
    # Shutdown (if needed)


app = FastAPI(lifespan=lifespan)

# Include route modules
app.include_router(vehicles.router)
app.include_router(bookings.router)
app.include_router(admin.router)
app.include_router(branches.router)
app.include_router(availability.router)
