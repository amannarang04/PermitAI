import traceback
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        try:
            return await call_next(request)
        except Exception as e:
            # Print traceback to console for server logs
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Internal Server Error",
                    "message": str(e)
                }
            )
