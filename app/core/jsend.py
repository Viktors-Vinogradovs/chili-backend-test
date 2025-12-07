from fastapi.responses import JSONResponse
from fastapi import status


def jsend_success(data=None, http_status: int = status.HTTP_200_OK):
    """
    JSend 'success' response.
    """
    if data is None:
        data = {}
    return JSONResponse(
        status_code=http_status,
        content={"status": "success", "data": data},
    )


def jsend_fail(data: dict, http_status: int = status.HTTP_400_BAD_REQUEST):
    """
    JSend 'fail' response, for 4xx errors (validation, bad input, etc.).
    """
    return JSONResponse(
        status_code=http_status,
        content={"status": "fail", "data": data},
    )


def jsend_error(message: str, http_status: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
    """
    JSend 'error' response, for unexpected server errors.
    """
    return JSONResponse(
        status_code=http_status,
        content={"status": "error", "message": message},
    )
