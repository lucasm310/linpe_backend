from starlette.requests import Request
from starlette.responses import Response

async def exceptions_handler(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        return Response(f"{e}", status_code=500)