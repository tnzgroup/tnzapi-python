import os

from tnzapi.core.legacy_kwargs import accept_legacy_kwargs


class TNZApiUser:

    @accept_legacy_kwargs({"auth_token": "AuthToken", "base_url": "BaseURL"})
    def __init__(self, AuthToken: str = None, BaseURL: str = None):

        AuthToken = AuthToken or os.environ.get("TNZ_AUTH_TOKEN")

        if not AuthToken:
            raise ValueError("AuthToken is required")

        self.AuthToken = AuthToken
        self.BaseURL = (BaseURL or os.environ.get("TNZ_API_URL") or "https://api.tnz.co.nz/api/v3.00").rstrip("/")
