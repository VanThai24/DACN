
from fastapi import FastAPI, Request
from backend_src.app.routers import employees, attendance, auth, faceid
import logging
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse





from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

# Mount static files for /photos (dùng đường dẫn tuyệt đối)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
PHOTOS_DIR = os.path.join(BASE_DIR, "wwwroot", "photos")
print("PHOTOS_DIR:", PHOTOS_DIR)
if not os.path.exists(PHOTOS_DIR):
    os.makedirs(PHOTOS_DIR)
app.mount("/photos", StaticFiles(directory=PHOTOS_DIR), name="photos")

# Rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# Rate limit error handler
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request, exc):
    return JSONResponse(status_code=429, content={"detail": "Too many requests, please try again later."})

# Thiết lập logging chi tiết
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

# Middleware logging request/response
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    try:
        response = await call_next(request)
    except Exception as exc:
        logger.error(f"Unhandled error: {exc}")
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})
    logger.info(f"Response status: {response.status_code}")
    return response

app.include_router(employees.router, prefix="/employees", tags=["employees"])
app.include_router(attendance.router, prefix="/attendance", tags=["attendance"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(faceid.router, prefix="/api/faceid")

@app.get("/")
def root():
    return {"message": "FaceID Attendance API"}
