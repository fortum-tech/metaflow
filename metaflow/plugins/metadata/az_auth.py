import atexit
import os

AUTH_PROFILE_ENV_VAR = "METAFLOW_AUTH_PROFILE"
OBO_TOKEN_ENV_VAR = "METAFLOW_OBO_TOKEN"


class AZAuth:
    _fetcher = None
    _cache = None

    def __init__(
        self,
        profile=os.environ.get(AUTH_PROFILE_ENV_VAR),
        obo_token=os.environ.get(OBO_TOKEN_ENV_VAR),
        cache=None,
    ):
        self.profile = profile
        self.obo_token = obo_token
        self._cache = cache

    @property
    def cache(self):
        if not self._cache:
            from az_app_login.util import load_cache, save_cache

            self._cache = load_cache()
            atexit.register(save_cache, self._cache)
        return self._cache

    @property
    def fetcher(self):
        if self.profile and not self._fetcher:
            from az_app_login.util import build_fetcher

            self._fetcher = build_fetcher(
                cache=self.cache, profile=self.profile, obo_token=self.obo_token
            )
        return self._fetcher

    def __call__(self, r):
        token = self.get_access_token()
        if not token:
            return r
        r.headers["Authorization"] = f"Bearer {token}"
        return r

    def get_access_token(self):
        if not self.fetcher:
            return None
        from az_app_login.util import get_access_token

        return get_access_token(self.fetcher)["access_token"]
