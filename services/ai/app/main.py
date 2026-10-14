from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.errors import ApiError
from app.routers.internal import router as internal_router

app = FastAPI()
app.include_router(internal_router)


@app.exception_handler(ApiError)
def handle_api_error(_request: Request, exc: ApiError):
    return JSONResponse(status_code=exc.status_code, content={"error": {"code": exc.code, "message": exc.message}})


@app.exception_handler(RequestValidationError)
def handle_validation_error(_request: Request, _exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"error": {"code": "validation_error", "message": "Проверьте заполненные поля"}},
    )
