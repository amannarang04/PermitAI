import time
import json
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from jose import jwt, JWTError

from app.database.session import SessionLocal
from app.models.audit_log import ApiActivityLog
from app.config import settings

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.time()
        
        # Safely read json request body if present
        body_bytes = b""
        if request.headers.get("content-type") == "application/json":
            try:
                body_bytes = await request.body()
                # Restore the receive channel so route handlers can read it
                async def receive():
                    return {"type": "http.request", "body": body_bytes, "more_body": False}
                request._receive = receive
            except Exception:
                pass
        
        response = await call_next(request)
        
        process_time_ms = int((time.time() - start_time) * 1000)
        
        # Log to DB asynchronously/synchronously (using local session)
        db = SessionLocal()
        try:
            # Extract user_id from JWT token if authorization header is present
            user_id = None
            auth_header = request.headers.get("authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
                try:
                    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
                    user_id = int(payload.get("sub"))
                except Exception:
                    pass

            # Extract request data
            req_data = None
            if body_bytes:
                try:
                    req_data = json.loads(body_bytes.decode("utf-8"))
                    # Mask password fields
                    if isinstance(req_data, dict):
                        for k in req_data.keys():
                            if "password" in k.lower():
                                req_data[k] = "********"
                except Exception:
                    pass

            # Create log entry
            log = ApiActivityLog(
                user_id=user_id,
                endpoint=str(request.url.path),
                method=request.method,
                status_code=response.status_code,
                response_time_ms=process_time_ms,
                request_data=req_data,
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent")
            )
            db.add(log)
            db.commit()
        except Exception as ex:
            print(f"[LoggingMiddleware Error] Failed to write API activity log: {ex}")
        finally:
            db.close()

        return response
