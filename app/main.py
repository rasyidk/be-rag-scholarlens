from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException as StarletteHTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.users import router as users_router
from app.api.v1.projects import router as projects_router
from app.api.v1.debug import router as debug_router
from app.api.v1.documents import router as documents_router
from app.utils.response import error_response

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
app.include_router(projects_router, prefix="/api/v1")
app.include_router(debug_router, prefix="/api/v1")
app.include_router(documents_router, prefix="/api/v1")


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    # If the exception detail is already a standardized response dict, return it as-is.
    detail = exc.detail
    if isinstance(detail, dict) and detail.get("status") in ("error", "success"):
        return JSONResponse(content=detail, status_code=exc.status_code)

    # Otherwise, wrap in standardized error response
    resp = error_response(message=str(detail), errors=[str(detail)], code=exc.status_code or 500)
    return JSONResponse(content=resp, status_code=exc.status_code or 500)

@app.get("/")
def hello_world():
    return {"message": "Hello, World!"}