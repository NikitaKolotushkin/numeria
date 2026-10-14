from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.errors import ApiError
from app.routers.auth import router as auth_router
from app.routers.internal import router as internal_router
from app.routers.me import router as me_router

app = FastAPI()
app.include_router(auth_router)
app.include_router(me_router)
app.include_router(internal_router)


@app.exception_handler(ApiError)
def handle_api_error(_request: Request, exc: ApiError):
    return JSONResponse(status_code=exc.status_code, content={"error": {"code": exc.code, "message": exc.message}})


@app.exception_handler(RequestValidationError)
def handle_validation_error(_request: Request, exc: RequestValidationError):
    invalid_json = any(error.get("type") in {"json_invalid", "json_decode"} for error in exc.errors())
    if invalid_json:
        return JSONResponse(
            status_code=400,
            content={"error": {"code": "validation_error", "message": "Тело запроса не разбирается"}},
        )
    return JSONResponse(
        status_code=422,
        content={"error": {"code": "validation_error", "message": "Проверьте заполненные поля"}},
    )
