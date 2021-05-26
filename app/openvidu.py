import json
import logging
from time import time
import requests

from datetime import datetime
from typing import List, Optional
from json import JSONDecodeError
from requests.api import head
from requests.auth import HTTPBasicAuth
from requests.models import Request


class OpenViduException(Exception):
    def __init__(self, status_code, error):
        if error:
            try:
                super().__init__('{}: {}'.format(status_code, json.loads(error)['message']))
            except (KeyError, JSONDecodeError):
                super().__init__('{}: {}'.format(status_code, error))
        else:
            super().__init__('{}: Unknown error'.format(status_code))


class Connection:
    def __init__(self, session, connection_data):
        self.session = session
        if isinstance(connection_data, str):
            connection_data = self._fetch(connection_data)
        self._data = connection_data

    def __repr__(self):
        return self.id

    @property
    def _logger(self) -> logging.Logger:
        return logging.getLogger('openvidu.Connection')

    def _fetch(self, _id=None):
        id = _id if _id else self.id
        response = self.session.server.request.get(f'sessions/{self.session.id}/connection/{id}')

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 400:
            raise OpenViduException(400, f'Session `{self.session.id}` does not exist.')
        elif response.status_code == 404:
            raise OpenViduException(404, f'Connection `{id}` does not exist.')
        else:
            response.raise_for_status()

    @property
    def id(self) -> str:
        return self._data['connectionId']

    @property
    def created_at(self) -> datetime:
        return datetime.utcfromtimestamp(self._data['createdAt'] / 1000)

    @property
    def type(self) -> str:
        return self._data['type']

    @property
    def role(self) -> Optional[str]:
        return self._data.get('role')

    @property
    def video_min_send_bandwidth(self) -> Optional[int]:
        if self._data['kurentoOptions'] and 'videoMinSendBandwidth' in 'kurentoOptions':
            return self._data['kurentoOptions']['videoMinSendBandwidth']
        else:
            return None

    @property
    def video_max_send_bandwidth(self) -> Optional[int]:
        if self._data['kurentoOptions'] and 'videoMaxSendBandwidth' in 'kurentoOptions':
            return self._data['kurentoOptions']['videoMaxSendBandwidth']
        else:
            return None

    @property
    def video_min_recv_bandwidth(self) -> Optional[int]:
        if self._data['kurentoOptions'] and 'videoMinRecvBandwidth' in 'kurentoOptions':
            return self._data['kurentoOptions']['videoMinRecvBandwidth']
        else:
            return None

    @property
    def video_max_recv_bandwidth(self) -> Optional[int]:
        if self._data['kurentoOptions'] and 'videoMaxRecvBandwidth' in 'kurentoOptions':
            return self._data['kurentoOptions']['videoMaxRecvBandwidth']
        else:
            return None

    @property
    def allowed_filters(self) -> Optional[list[str]]:
        if self._data['kurentoOptions'] and 'allowedFilters' in 'kurentoOptions':
            return self._data['kurentoOptions']['allowedFilters']
        else:
            return None

    @property
    def rtsp_uri(self) -> Optional[str]:
        return self._data.get('rtspUri')

    @property
    def adaptive_bitrate(self) -> Optional[bool]:
        return self._data.get('adaptativeBitrate')

    @property
    def only_play_with_subscribers(self) -> Optional[bool]:
        return self._data.get('onlyPlayWithSubscribers')

    @property
    def network_cache(self) -> Optional[int]:
        return self._data.get('networkCache')

    @property
    def token(self) -> str:
        return self._data['token']

    @property
    def platform(self) -> Optional[str]:
        return self._fetch().get('platform')

    @property
    def client_data(self) -> Optional[str]:
        return self._fetch().get('clientData')

    @property
    def publishers(self) -> Optional[List[dict]]:
        return self._fetch().get('publishers')

    @property
    def subscribers(self) -> Optional[List[dict]]:
        return self._fetch().get('subscribers')

    def disconnect(self):
        response = self.session.server.request.delete(f'sessions/{self.session.id}/connection/{self.id}')

        if response.status_code == 204:
            self._logger.info(f'Connection `{self.id}` in Session `{self.session.id}` closed')
        elif response.status_code == 400:
            raise OpenViduException(response.status_code, f'Session `{self.session.id}` does not exist')
        elif response.status_code == 404:
            raise OpenViduException(response.status_code, f'Connection `{self.id}` does not exist')
        else:
            response.raise_for_status()


class Recording:
    def __init__(self, session, recording_data):
        self.session = session
        if isinstance(recording_data, str):
            recording_data = self._fetch(recording_data)
        self._data = recording_data

    def __repr__(self):
        return self.id

    @property
    def id(self) -> str:
        return self._data['id']

    @property
    def name(self) -> str:
        return self._data['name']

    @property
    def output_mode(self) -> str:
        return self._data['outputMode']

    @property
    def has_audio(self) -> bool:
        return self._data['hasAudio']

    @property
    def has_video(self) -> bool:
        return self._data['hasVideo']

    @property
    def recording_layout(self) -> Optional[str]:
        return self._data.get('recordingLayout')

    @property
    def custom_layout(self) -> Optional[str]:
        return self._data.get('customLayout')

    @property
    def resolution(self) -> Optional[str]:
        return self._data.get('resolution')

    @property
    def created_at(self) -> datetime:
        return datetime.utcfromtimestamp(self._data['createdAt'] / 1000)

    @property
    def size(self) -> Optional[int]:
        data = self._fetch()
        if data['status'] == 'ready':
            return data['size']
        else:
            return None

    @property
    def duration(self) -> Optional[float]:
        data = self._fetch()
        if data['status'] == 'ready':
            return data['duration']
        else:
            return None

    @property
    def url(self) -> Optional[str]:
        data = self._fetch()
        if data['status'] == 'ready':
            return data['url']
        else:
            return None

    @property
    def status(self) -> str:
        return self._fetch()['status']

    def _fetch(self, _id=None):
        id = _id if _id else self.id
        response = self.session.server.request.get(f'recordings/{id}')

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            raise OpenViduException(404, f'Recording `{id}` does not exist.')
        elif response.status_code == 501:
            raise OpenViduException(501, 'OpenVidu Server recording module is disabled')
        else:
            response.raise_for_status()

    def stop(self):
        response = self.session.server.request.post(f'recordings/stop/{self.id}')

        if response.status_code == 200:
            self._logger.info(f'Recording of session `{self.id}` stopped')
        elif response.status_code == 404:
            raise OpenViduException(response.status_code, f'Recording `{self.id}` does not exist')
        elif response.status_code == 406:
            raise OpenViduException(406, 'Recording has starting status. Wait until started status before stopping the recording')
        elif response.status_code == 501:
            raise OpenViduException(501, 'OpenVidu Server recording module is disabled')
        else:
            response.raise_for_status()

    @property
    def _logger(self) -> logging.Logger:
        return logging.getLogger('openvidu.Recording')


class Session:
    def __init__(self, server, session_data):
        self.server = server
        if isinstance(session_data, str):
            session_data = self._fetch(session_data)
        self._data = session_data

    def __repr__(self):
        return self.id

    @property
    def id(self) -> str:
        return self._data['sessionId']

    @property
    def custom_session_id(self) -> str:
        return self._data['customSessionId'] if self._data['customSessionId'] != '' else None

    @property
    def created_at(self) -> datetime:
        return datetime.utcfromtimestamp(self._data['createdAt'] / 1000)

    @property
    def media_mode(self) -> str:
        return self._data['mediaMode']

    @property
    def recording_mode(self) -> str:
        return self._data['recordingMode']

    @property
    def default_output_mode(self) -> str:
        return self._data['defaultOutputMode']

    @property
    def default_recording_layout(self) -> str:
        return self._data['defaultRecordingLayout']

    @property
    def default_custom_layout(self) -> Optional[str]:
        return self._data.get('defaultCustomLayout')

    @property
    def transcoding_allowed(self) -> str:
        return self._data['allowTranscoding']

    @property
    def recording(self) -> bool:
        return self._fetch()['recording']

    @property
    def connections(self) -> List[Connection]:
        return [Connection(self.server, self.id, connection) for connection in self._fetch()['connections']['content']]

    def close(self):
        response = self.server.request.delete(f'sessions/{self.id}')

        if response.status_code == 204:
            self._logger.info(f'Session `{self.id}` has been closed')
        elif response.status_code == 404:
            raise OpenViduException(404, f'Session `{self.id}` does not exist.')
        else:
            response.raise_for_status()

    def create_connection(
            self,
            type=None,
            data=None,
            role=None,
            video_min_send_bandwidth=None,
            video_max_send_bandwidth=None,
            video_min_recv_bandwidth=None,
            video_max_recv_bandwidth=None,
            allowed_filters=None,
            rtsp_uri=None,
            adaptive_bitrate=None,
            only_play_with_subscribers=None,
            network_cache=None) -> Connection:

        kurento_options = {}
        if video_min_send_bandwidth:
            kurento_options['videoMinSendBandwidth'] = video_min_send_bandwidth
        if video_max_send_bandwidth:
            kurento_options['videoMaxSendBandwidth'] = video_max_send_bandwidth
        if video_min_recv_bandwidth:
            kurento_options['videoMinRecvBandwidth'] = video_min_recv_bandwidth
        if video_max_recv_bandwidth:
            kurento_options['videoMaxRecvBandwidth'] = video_max_recv_bandwidth
        if allowed_filters:
            kurento_options['allowedFilters'] = allowed_filters
        response = self.server.request.post(f'sessions/{self.id}/connection', json=dict(
            type=type,
            data=data,
            role=role,
            kurentoOptions=kurento_options if len(kurento_options) > 0 else None,
            rtspUri=rtsp_uri,
            adaptativeBitrate=adaptive_bitrate,
            onlyPlayWithSubscribers=only_play_with_subscribers,
            networkCache=network_cache
        ))

        if response.status_code == 200:
            connection = response.json()
            self._logger.info(f'Created new connection `{connection["id"]}` in Session `{self.id}`')
            return Connection(self, connection)
        elif response.status_code == 400 or response.status_code == 404 or response.status_code == 500:
            raise OpenViduException(response.status_code, response.content.decode('utf-8'))
        else:
            raise response.raise_for_status()

    def signal(self, to=None, type=None, data=None):
        if to:
            if isinstance(to, list):
                to = [str(t) for t in to]
            else:
                to = [str(to)]

        response = self.server.request.post('signal', json=dict(
            session=self.id,
            to=to,
            type=type,
            data=data,
        ))

        if response.status_code == 200:
            return
        elif response.status_code == 404:
            raise OpenViduException(404, f'Session `{self.id}` does not exist.')
        elif response.status_code == 406:
            if not to:
                raise OpenViduException(406, "No connection exists for the session")
            else:
                raise OpenViduException(
                    406,
                    "No connection exists for provided connections or some string value that does not "
                    "correspond to a valid connection of the session (even though others may be correct)")
        elif response.status_code == 400:
            raise OpenViduException(response.status_code, response.content.decode('utf-8'))
        else:
            raise response.raise_for_status()

    def start_recording(self, name = None, output_mode=None, has_audio=None, has_video=None, recording_layout=None, custom_layout=None, resolution=None) -> Recording:
        response = self.server.request.post(f'{self.server.url}recordings/start', json=dict(
            session=self.id,
            name=name,
            outputMode=output_mode,
            hasAudio=has_audio,
            hasVideo=has_video,
            recordingLayout=recording_layout,
            customLayout=custom_layout,
            resolution=resolution
        ))

        if response.status_code == 200:
            self._logger.info('Recording of session `%s` started', self.id)
            return Recording(self.server, response.json())
        elif response.status_code == 400:
            raise OpenViduException(400, response.content.decode('utf-8'))
        elif response.status_code == 422:
            raise OpenViduException(422, '`resolution` exceeds accaptable values')
        elif response.status_code == 404:
            raise OpenViduException(404, f'Session `{self.id}` does not exist')
        elif response.status_code == 406:
            raise OpenViduException(406, f'Session `{self.id}` does not have connected participants')
        elif response.status_code == 501:
            raise OpenViduException(501, 'OpenVidu Server recording module is disabled')
        else:
            response.raise_for_status()

    def _fetch(self, _id=None):
        id = _id if _id else self.id
        response = self.server.request.get(f'sessions/{id}')

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            raise OpenViduException(404, f'Session `{id}` does not exist.')
        else:
            response.raise_for_status()

    @property
    def _logger(self) -> logging.Logger:
        return logging.getLogger('openvidu.Session')


class Server:
    @property
    def request(self) -> requests.Session:
        class RequestSession(requests.Session):
            def __init__(self, url, secret, timeout, verify):
                self._url = url
                self._headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
                self._auth = HTTPBasicAuth('OPENVIDUAPP', secret)
                self._verify = verify
                self._timeout = timeout
                super().__init__()

            def request(self, method, endpoint, **kwargs) -> requests.Response:
                return super().request(
                    method,
                    f'{self._url}/openvidu/api/{endpoint}',
                    headers=self._headers,
                    auth=self._auth,
                    verify=self._verify,
                    timeout=self._timeout,
                    **kwargs)

        return RequestSession(self._request_url, self._request_secret, self._request_timeout, self._request_verify)

    def __init__(self, url, secret, timeout=None, verify=True):
        self._request_url = url
        self._request_secret = secret
        self._request_timeout = timeout
        self._request_verify = verify

    def __repr__(self):
        return f'<OpenVidu "{self._request_url}">'

    @property
    def config(self) -> dict:
        response = self.request.get('config')

        if response.status_code == 200:
            data = response.json()

            return dict(
                version=data['VERSION'],
                domain_or_public_ip=data['DOMAIN_OR_PUBLIC_IP'],
                https_port=data['HTTPS_PORT'],
                public_url=data['OPENVIDU_PUBLICURL'],
                cdr=data["OPENVIDU_CDR"],
                streams=dict(video=dict(
                    min_send_bandwith=data['OPENVIDU_STREAMS_VIDEO_MIN_SEND_BANDWIDTH'],
                    max_send_bandwith=data['OPENVIDU_STREAMS_VIDEO_MAX_SEND_BANDWIDTH'],
                    min_recv_bandwith=data['OPENVIDU_STREAMS_VIDEO_MIN_RECV_BANDWIDTH'],
                    max_recv_bandwith=data['OPENVIDU_STREAMS_VIDEO_MAX_RECV_BANDWIDTH'],
                )),
                recording=dict(
                    version=data['OPENVIDU_RECORDING_VERSION'],
                    path=data['OPENVIDU_RECORDING_PATH'],
                    public_access=data['OPENVIDU_RECORDING_PUBLIC_ACCESS'],
                    notification=data['OPENVIDU_RECORDING_NOTIFICATION'],
                    custom_layout=data['OPENVIDU_RECORDING_CUSTOM_LAYOUT'],
                    autostop_timeout=data['OPENVIDU_RECORDING_AUTOSTOP_TIMEOUT'],
                ) if data['OPENVIDU_RECORDING'] else None,
                webhook=dict(
                    endpoint=data['OPENVIDU_WEBHOOK_ENDPOINT'],
                    headers=data['OPENVIDU_WEBHOOK_HEADERS'],
                    events=data['OPENVIDU_WEBHOOK_EVENTS'],
                ) if data['OPENVIDU_WEBHOOK'] else None
            )
        else:
            response.raise_for_status()

    def initialize_session(
            self,
            media_mode=None,
            recording_mode=None,
            custom_session_id=None,
            default_output_mode=None,
            default_recording_layout=None,
            default_custom_layout=None,
            forced_video_codec=None,
            allow_transcoding=None) -> Session:
        response = self.request.post(f'sessions', json=dict(
                                     mediaMode=media_mode,
                                     recordingMode=recording_mode,
                                     customSessionId=custom_session_id,
                                     defaultOutputMode=default_output_mode,
                                     defaultRecordingLayout=default_recording_layout,
                                     defaultCustomLayout=default_custom_layout,
                                     forcedVideoCodec=forced_video_codec,
                                     allowTranscoding=allow_transcoding
                                     ))

        if response.status_code == 200:
            session = response.json()
            self._logger.info(f'Created new session `{session["id"]}`')
            return Session(self, session)
        elif response.status_code == 409:
            self._logger.info(f'Using existing session `{custom_session_id}`')
            return Session(self, custom_session_id)
        elif response.status_code == 400:
            raise OpenViduException(response.status_code, response.content.decode('utf-8'))
        else:
            raise response.raise_for_status()

    @property
    def sessions(self) -> List[Session]:
        response = self.request.get('sessions')

        if response.status_code == 200:
            return [Session(self, session) for session in response.json()['content']]
        else:
            raise response.raise_for_status()

    @property
    def _logger(self) -> logging.Logger:
        return logging.getLogger('openvidu.Server')
