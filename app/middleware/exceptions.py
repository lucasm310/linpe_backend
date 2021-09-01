from starlette.requests import Request
from starlette.responses import Response

from app.helpers.logger import get_logger

async def exceptions_handler(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        log = get_logger()
        log.critical(f"error={e}")
        return Response(f"{e}", status_code=500)