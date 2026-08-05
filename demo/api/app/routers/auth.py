import os
import secrets

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

router = APIRouter(prefix="/api/auth")

_SESSION_COOKIE = "demo_session_id"
# Server-side only, keyed by an opaque per-browser session id - never the token itself. Unlike
# Starlette's SessionMiddleware (which signs but does not encrypt its cookie, making the raw
# stored value readable client-side), the real TNZ bearer token never leaves this process.
#
# Single-process only, by design: this dict is process-local, so it only works correctly with
# uvicorn's default single worker (matching the Dockerfile's CMD, which has no --workers flag).
# A multi-worker or multi-replica deployment would need a shared store instead - out of scope
# for a local dev demo.
_TOKEN_OVERRIDES: dict[str, str] = {}
_MAX_TOKEN_OVERRIDES = 1000


class SetTokenRequest(BaseModel):
    Token: str


def resolve_auth_token(request: Request) -> str:
    session_id = request.cookies.get(_SESSION_COOKIE)
    if session_id and session_id in _TOKEN_OVERRIDES:
        return _TOKEN_OVERRIDES[session_id]
    return os.environ.get("TNZ_AUTH_TOKEN", "")


@router.post("/token")
async def set_token(request: Request, body: SetTokenRequest):
    token = body.Token

    if not token or len(token.split(".")) != 3:
        return JSONResponse(
            status_code=400,
            content={
                "Result": "Failed",
                "ErrorMessage": ["Token must be a non-empty value with three dot-separated segments (a JWT shape)."],
            },
        )

    # Always mint a fresh session id here rather than reusing any cookie value the caller
    # already sent - trusting a caller-supplied id as the storage key would let an attacker
    # plant a known demo_session_id in a victim's browser ahead of time (session fixation),
    # then read the victim's real token back out under that same known id later.
    old_session_id = request.cookies.get(_SESSION_COOKIE)
    if old_session_id is not None:
        _TOKEN_OVERRIDES.pop(old_session_id, None)

    if len(_TOKEN_OVERRIDES) >= _MAX_TOKEN_OVERRIDES:
        _TOKEN_OVERRIDES.pop(next(iter(_TOKEN_OVERRIDES)))

    session_id = secrets.token_urlsafe(32)
    _TOKEN_OVERRIDES[session_id] = token

    response = JSONResponse(content={"Status": "ok"})
    response.set_cookie(
        _SESSION_COOKIE,
        session_id,
        httponly=True,
        samesite="lax",
        secure=os.environ.get("TNZ_ALLOW_INSECURE_HTTP", "").lower() != "true",
    )
    return response
