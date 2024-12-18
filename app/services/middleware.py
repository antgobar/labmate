from typing import Callable

from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import PUBLIC_ENDPOINTS
from app.services.crud.auth import get_current_user
from app.services.database import get_db
from app.services.models import UserRole


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        self.app = app
        super().__init__(app)

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ):
        endpoint = request.url.path.split("/")[1]
        db = next(get_db())
        user = get_current_user(request, db)

        if endpoint == UserRole.ADMIN.name.lower():
            if user is not None and user.role == UserRole.ADMIN.name:
                response = await call_next(request)
                return response
            return RedirectResponse(url="/login", status_code=303)

        if endpoint not in PUBLIC_ENDPOINTS:
            if user is not None:
                response = await call_next(request)
                return response
            return RedirectResponse(url="/login", status_code=303)

        response = await call_next(request)
        return response


# class CacheControlMiddleware(BaseHTTPMiddleware):
#     async def dispatch(self, request: Request, call_next):
#         endpoint = request.url.path.split("/")[1]
#         response = await call_next(request)
#         if endpoint in ["about", "contact", "pricing"]:
#             response.headers["Cache-Control"] = "public, max-age=3600"
#         return response
