from requests.exceptions import RequestException

from modules import util
from modules.util import Failed

logger = util.logger


class Seerr:
    def __init__(self, requests, params):
        self.requests = requests
        self.url = params["url"].rstrip("/")
        self.api_key = params["apikey"]
        logger.secret(self.url)
        logger.secret(self.api_key)

    def request(self, media_type, media_id, is4k=False, tvdb_id=None, overrides=None):
        payload = {"mediaType": media_type, "mediaId": int(media_id), "is4k": is4k}
        if media_type == "tv":
            payload["seasons"] = "all"
            if tvdb_id is not None:
                payload["tvdbId"] = int(tvdb_id)
        request_overrides = overrides or {}
        for key, value in request_overrides.items():
            if key == "server_id":
                payload["serverId"] = value
            elif key == "root_folder":
                payload["rootFolder"] = value
            elif key == "quality_profile":
                if isinstance(value, int):
                    payload["profileId"] = value
                else:
                    payload["profileName"] = value

        url = f"{self.url}/api/v1/request"
        try:
            response = self.requests.post(url, json=payload, headers={"X-Api-Key": self.api_key})
            if response.status_code in [202, 409]:
                try:
                    result = response.json()
                    message = result.get("message", response.text) if isinstance(result, dict) else response.text
                except ValueError:
                    message = response.text
                return {"_kometa_status": "duplicate" if response.status_code == 409 else "skipped", "message": message}
            if response.status_code < 200 or response.status_code >= 300:
                try:
                    error = response.json()
                    message = error.get("message", error.get("error", response.text)) if isinstance(error, dict) else response.text
                except ValueError:
                    message = response.text
                raise Failed(f"Seerr Error: Request failed with status {response.status_code}: {message}")
            try:
                return response.json()
            except ValueError as error:
                raise Failed("Seerr Error: Request succeeded but returned invalid JSON") from error
        except Failed:
            raise
        except RequestException as error:
            raise Failed(f"Seerr Error: Request failed: {error}") from error
