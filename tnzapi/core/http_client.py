import os
import requests

from tnzapi.core.auth import TNZApiUser

USER_AGENT = "tnzapi-python/3.00"
DEFAULT_TIMEOUT_SECONDS = 30


class HttpClient:

    def __init__(self, user: TNZApiUser):
        self.user = user
        self._session = requests.Session()

    def close(self):
        self._session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.user.AuthToken}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": USER_AGENT,
        }

    def _full_url(self, path: str) -> str:

        url = f"{self.user.BaseURL}{path}"

        if not url.startswith("https://") and os.environ.get("TNZ_ALLOW_INSECURE_HTTP") != "true":
            raise ValueError(
                "TNZ API URL must use HTTPS - refusing to send the Authorization "
                "bearer token over plain HTTP. Set TNZ_ALLOW_INSECURE_HTTP=true to override for local dev."
            )

        return url

    def get(self, path: str) -> requests.Response:
        return self._session.get(self._full_url(path), headers=self._headers(), timeout=DEFAULT_TIMEOUT_SECONDS)

    def post(self, path: str, json_body: dict) -> requests.Response:
        return self._session.post(self._full_url(path), json=json_body, headers=self._headers(), timeout=DEFAULT_TIMEOUT_SECONDS)

    def patch(self, path: str, json_body: dict) -> requests.Response:
        return self._session.patch(self._full_url(path), json=json_body, headers=self._headers(), timeout=DEFAULT_TIMEOUT_SECONDS)

    def delete(self, path: str) -> requests.Response:
        return self._session.delete(self._full_url(path), headers=self._headers(), timeout=DEFAULT_TIMEOUT_SECONDS)
