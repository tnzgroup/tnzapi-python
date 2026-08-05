import os
from urllib.parse import urlparse

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

router = APIRouter(prefix="/api/settings")


class SetApiUrlRequest(BaseModel):
    ApiUrl: str


class SetAllowInsecureHttpRequest(BaseModel):
    Enabled: bool


class SetSslVerificationRequest(BaseModel):
    Enabled: bool


def _is_valid_http_url(value: str) -> bool:
    try:
        parsed = urlparse(value)
    except ValueError:
        return False
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)


def _ssl_verification_not_supported() -> JSONResponse:
    return JSONResponse(
        status_code=501,
        content={
            "Result": "Failed",
            "ErrorMessage": [
                "tnzapi-python's HttpClient has no SSL certificate verification toggle - "
                "this setting has nothing to control on this backend."
            ],
        },
    )


@router.get("/api-url")
async def get_api_url():
    return {"ApiUrl": os.environ.get("TNZ_API_URL", "https://api.tnz.co.nz/api/v3.00")}


@router.post("/api-url")
async def set_api_url(body: SetApiUrlRequest):
    if not body.ApiUrl or not _is_valid_http_url(body.ApiUrl):
        return JSONResponse(
            status_code=400,
            content={"Result": "Failed", "ErrorMessage": [f"Invalid ApiUrl: '{body.ApiUrl}'"]},
        )

    if urlparse(body.ApiUrl).scheme == "http" and os.environ.get("TNZ_ALLOW_INSECURE_HTTP", "").lower() != "true":
        return JSONResponse(
            status_code=400,
            content={
                "Result": "Failed",
                "ErrorMessage": ["ApiUrl must use https:// unless TNZ_ALLOW_INSECURE_HTTP=true is set."],
            },
        )

    os.environ["TNZ_API_URL"] = body.ApiUrl
    return {"Status": "ok", "ApiUrl": body.ApiUrl}


@router.get("/allow-insecure-http")
async def get_allow_insecure_http():
    return {"Enabled": os.environ.get("TNZ_ALLOW_INSECURE_HTTP", "").lower() == "true"}


@router.post("/allow-insecure-http")
async def set_allow_insecure_http(body: SetAllowInsecureHttpRequest):
    os.environ["TNZ_ALLOW_INSECURE_HTTP"] = "true" if body.Enabled else "false"
    return {"Status": "ok", "Enabled": body.Enabled}


@router.get("/ssl-verification")
async def get_ssl_verification():
    return _ssl_verification_not_supported()


@router.post("/ssl-verification")
async def set_ssl_verification(body: SetSslVerificationRequest):
    return _ssl_verification_not_supported()
