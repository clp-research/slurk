from werkzeug.http import HTTP_STATUS_CODES
import requests

from requests.auth import HTTPBasicAuth


class OpenVidu:
    def __init__(self, url, secret, timeout=None, verify=True):
        self._request_url = url
        self._request_secret = secret
        self._request_timeout = timeout
        self._request_verify = verify

    def __repr__(self):
        return f'<OpenVidu "{self._request_url}">'

    @property
    def _request(self) -> requests.Session:
        class RequestSession(requests.Session):
            def __init__(self, url, secret, timeout, verify):
                self._url = url
                self._headers = {
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                }
                self._auth = HTTPBasicAuth("OPENVIDUAPP", secret)
                self._verify = verify
                self._timeout = timeout
                super().__init__()

            def request(self, method, endpoint, **kwargs) -> requests.Response:
                return super().request(
                    method,
                    f"{self._url}/openvidu/api/{endpoint}",
                    headers=self._headers,
                    auth=self._auth,
                    verify=self._verify,
                    timeout=self._timeout,
                    **kwargs,
                )

        return RequestSession(
            self._request_url,
            self._request_secret,
            self._request_timeout,
            self._request_verify,
        )

    def list_sessions(self):
        return self._request.get("sessions")

    def get_session(self, session_id):
        return self._request.get(f"sessions/{session_id}")

    def post_session(self, json):
        return self._request.post("sessions", json=json)

    def delete_session(self, session_id):
        return self._request.delete(f"sessions/{session_id}")

    def signal(self, session_id, json):
        json["session"] = session_id
        return self._request.post("signal", json=json)

    def list_connections(self, session_id):
        return self._request.get(f"sessions/{session_id}/connection")

    def get_connection(self, session_id, connection_id):
        return self._request.get(f"sessions/{session_id}/connection/{connection_id}")

    def post_connection(self, session_id, json):
        return self._request.post(f"sessions/{session_id}/connection", json=json)

    def delete_connection(self, session_id, connection_id):
        return self._request.delete(f"sessions/{session_id}/connection/{connection_id}")

    def start_recording(self, session_id, json):
        json["session"] = session_id
        return self._request.post("recordings/start", json=json)

    def stop_recording(self, recording_id):
        return self._request.post(f"recordings/stop/{recording_id}")

    def get_recording(self, recording_id):
        return self._request.get(f"recordings/{recording_id}")

    def list_recordings(self):
        return self._request.get("recordings")

    def delete_recording(self, recording_id):
        return self._request.delete(f"recordings/{recording_id}")


def init_app(app):
    if "OPENVIDU_URL" in app.config:
        openvidu_url = app.config["OPENVIDU_URL"]
        openvidu_port = app.config["OPENVIDU_PORT"]
        openvidu_secret = app.config.get("OPENVIDU_SECRET")
        openvidu_verify = app.config.get("OPENVIDU_VERIFY", True)
        if not openvidu_secret:
            raise ValueError(
                "OpenVidu Secret key not provided. Pass `SLURK_OPENVIDU_SECRET` as environment variable."
            )

        if openvidu_port != 443:
            openvidu_url = f"{openvidu_url}:{openvidu_port}"
        OV = OpenVidu(openvidu_url, openvidu_secret, verify=openvidu_verify)
        response = OV._request.get("config")
        if response.status_code != 200:
            error = HTTP_STATUS_CODES.get(response.status_code, "Unknown Error")
            app.logger.error(
                f'Could not connection to OpenVidu Server "{openvidu_url}: {error})'
            )
            return

        OV.config = response.json()
        app.logger.info(f'Initializing OpenVidu connection to "{openvidu_url}"')
        if not openvidu_verify:
            app.logger.warning(
                "OpenVidu connection may be unsecure. Set `SLURK_OPENVIDU_VERIFY` to true or don't pass this variable"
            )
        app.openvidu = OV
