# app/core/error_handlers.py

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from app.core.jsend import jsend_fail, jsend_error


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request,
        exc: StarletteHTTPException,
    ):
        """
        Wrap all HTTPException responses into JSend.

        4xx  -> status=fail
        5xx+ -> status=error
        """
        status_code = exc.status_code

        # 4xx → fail
        if 400 <= status_code < 500:
            # detail might be a string or dict
            if isinstance(exc.detail, dict):
                data = exc.detail
            else:
                data = {"detail": str(exc.detail)}

            return jsend_fail(data=data, http_status=status_code)

        # 5xx → error
        return jsend_error(
            message=str(exc.detail),
            http_status=status_code,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ):
        """
        Body/query/path validation errors (422) -> JSend fail.
        """
        return jsend_fail(
            data={"errors": exc.errors()},
            http_status=422,
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request,
        exc: Exception,
    ):
        """
        Catch-all for unexpected errors -> JSend error.
        """
        # You can also log `exc` here if you want.
        return jsend_error(
            message="Internal server error",
            http_status=HTTP_500_INTERNAL_SERVER_ERROR,
        )
