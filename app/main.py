from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.users import router as users_router

app = FastAPI()

# Add CORS middleware (allow all for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users_router, prefix="/api/v1")

@app.get("/")
def hello_world():
    return {"message": "Hello, World!"}