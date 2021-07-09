import marshmallow as ma
from marshmallow.validate import OneOf, Range

from slurk.views.api import BaseSchema
from slurk.views.api.openvidu.fields import String, List, Timestamp, SessionId, Resolution, IntegerOrNone


class StreamsConfigSchema(BaseSchema):
    videoMaxRecvBandwidth = ma.fields.Integer(
        data_key='video_max_recv_bandwith',
        description='Maximum video bandwidth sent from clients to OpenVidu Server, in kbps. 0 means unconstrained')
    videoMaxSendBandwidth = ma.fields.Integer(
        data_key='video_max_send_bandwith',
        description='Maximum video bandwidth sent from OpenVidu Server to clients, in kbps. 0 means unconstrained')
    videoMinRecvBandwidth = ma.fields.Integer(
        data_key='video_min_recv_bandwith',
        description='Minimum video bandwidth sent from clients to OpenVidu Server, in kbps. 0 means unconstrained')
    videoMinSendBandwidth = ma.fields.Integer(
        data_key='video_min_send_bandwith',
        description='Minimum video bandwidth sent from OpenVidu Server to clients, in kbps. 0 means unconstrained')


class SessionsConfigSchema(BaseSchema):
    garbage_interval = ma.fields.Integer(
        description='How often the garbage collector of non active sessions runs')
    garbage_threshold = ma.fields.Integer(
        description='Minimum time in seconds that a non active session must have been in existence for the garbage collector of non active sessions to remove it')


class RecordingConfigSchema(BaseSchema):
    version = ma.fields.String(
        description='Version of the recording')
    path = ma.fields.String(
        description='System path where to store the video files of recorded sessions')
    public_access = ma.fields.Boolean(
        description='Whether to allow free http access to recorded sessions or not')
    notification = ma.fields.String(
        description='Which users should receive the recording events in the client side')
    custom_layout = ma.fields.String(
        description='System path where OpenVidu Server should look for custom recording layouts')
    autostop_timeout = ma.fields.Integer(
        description='Timeout in seconds for recordings to automatically stop when conditions are met')


class WebhookConfigSchema(BaseSchema):
    endpoints = ma.fields.List(
        ma.fields.String(),
        description='HTTP endpoint where OpenVidu Server will send the POST messages with webhook events')
    headers = ma.fields.List(
        ma.fields.String(),
        description='HTTP headers that OpenVidu Server will append to each POST message of webhook events')
    events = ma.fields.List(
        ma.fields.String(),
        description='Type of events OpenVidu Server will send to your webhook')


class ConfigSchema(BaseSchema):
    version = ma.fields.String(
        description='Version of the OpenVidu Server')
    domain_or_public_ip = ma.fields.String(
        description='Domain name where OpenVidu Server is available')
    https_port = ma.fields.Integer(
        description='Secure port where OpenVidu Server is listening')
    public_url = ma.fields.String(
        description='URL where OpenVidu Server is available')
    cdr = ma.fields.Boolean(
        description='Call Detail Record is enabled')
    streams = ma.fields.Nested(
        StreamsConfigSchema,
        description='Configuration for streams')
    sessions = ma.fields.Nested(
        SessionsConfigSchema,
        description='Default configuration for sessions')
    recording = ma.fields.Nested(
        RecordingConfigSchema,
        allow_none=True,
        description='Configuration for recordings')
    webhook = ma.fields.Nested(
        WebhookConfigSchema,
        allow_none=True,
        description='Configuration for webhooks')


class DefaultRecordingPropertiesSchema(BaseSchema):
    name = String(
        missing=None,
        description='Name of the Recording')
    outputMode = ma.fields.String(
        data_key='output_mode',
        validate=OneOf(['COMPOSED', 'INDIVIDUAL', 'COMPOSED_QUICK_START']),
        missing='COMPOSED',
        description='Output mode of the Recording')
    hasAudio = ma.fields.Boolean(
        data_key='has_audio',
        missing=True,
        description='True if the Recording includes an audio track, false otherwise')
    hasVideo = ma.fields.Boolean(
        data_key='has_video',
        missing=True,
        description='True if the Recording includes a video track, false otherwise')
    recordingLayout = ma.fields.String(
        data_key='recording_layout',
        validate=OneOf(['BEST_FIT', 'CUSTOM']),
        missing='BEST_FIT',
        description='The recording layout that is being used')
    resolution = Resolution(
        missing="1280x720",
        description='Resolution of the video file')
    frameRate = ma.fields.Integer(
        data_key='frame_rate',
        missing=30,
        validate=Range(min=1, max=120),
        description='Frame rate of the video file')
    shmSize = ma.fields.Integer(
        missing=536870912,
        load_only=True,
        description='The amount of memory dedicated to the recording module in charge of this specific recording, in bytes')


# Extra class to keep ordering
class RecordingPropertiesSchema(BaseSchema):
    id = ma.fields.String(
        dump_only=True,
        description='Identifier of the Recording')


class RecordingSchema(RecordingPropertiesSchema, DefaultRecordingPropertiesSchema):
    ignoreFailedStreams = ma.fields.Boolean(
        data_key='ignore_failed_streams',
        missing=False,
        description='Whether to ignore failed streams or not when starting the recording')
    sessionId = SessionId(
        data_key='session_id',
        dump_only=True,
        description='Session associated to the Recording')
    customLayout = ma.fields.String(
        data_key='custom_layout',
        missing=None,
        description='The custom layout that is being used')
    createdAt = Timestamp(
        data_key='created_at',
        dump_only=True,
        description='Time when the recording started')
    size = IntegerOrNone(
        dump_only=True,
        description='Size in bytes of the video file. Only guaranteed to be greater than 0 if status is `ready`')
    duration = IntegerOrNone(
        dump_only=True,
        description='Duration of the video file in seconds. Only guaranteed to be greater than 0 if status is `ready`')
    url = String(
        dump_only=True,
        allow_none=True,
        description='URL where the Recording file is available. Only guaranteed to be set if status is `ready`')
    status = ma.fields.String(
        dump_only=True,
        validate=OneOf(['starting', 'started', 'stopped', 'ready', 'failed']),
        description='Status of the Recording')


class VideoDimensionsSchema(BaseSchema):
    width = ma.fields.Integer(
        description='Width of the video')
    height = ma.fields.Integer(
        description='Height of the video')

    def _serialize(self, obj, many=None, **kwargs):
        import json

        if isinstance(obj, str):
            return json.loads(obj)
        return super()._serialize(obj, many, **kwargs)


class MediaOptionsSchema(BaseSchema):
    hasVideo = ma.fields.Boolean(
        data_key='has_video',
        dump_only=True,
        description='True if the stream has a video track, false otherwise')
    hasAudio = ma.fields.Boolean(
        data_key='has_audio',
        dump_only=True,
        description='True if the stream has an audio track, false otherwise')
    videoActive = ma.fields.Boolean(
        data_key='video_active',
        dump_only=True,
        description='True if the video track is active, false otherwise')
    audioActive = ma.fields.Boolean(
        data_key='audio_active',
        dump_only=True,
        description='True if the audio track is active, false otherwise')
    frameRate = ma.fields.Integer(
        data_key='frame_rate',
        dump_only=True,
        description='The frame rate of the stream')
    videoDimensions = ma.fields.Nested(
        VideoDimensionsSchema,
        data_key='video_dimensions',
        dump_only=True,
        description='The video dimensions of the stream')
    typeOfVideo = ma.fields.String(
        data_key='type_of_video',
        dump_only=True,
        description='The type of video')
    filter = ma.fields.Dict(
        dump_only=True,
        description='Filter used for the stream')


class PublisherSchema(BaseSchema):
    streamId = ma.fields.String(
        data_key='stream_id',
        dump_only=True,
        description='Identifier of the stream')
    createdAt = Timestamp(
        data_key='created_at',
        dump_only=True,
        description='Time when the stream was published')
    mediaOptions = ma.fields.Nested(
        MediaOptionsSchema,
        data_key='media_options',
        dump_only=True,
        description='Current properties of the published stream')


class SubscriberSchema(BaseSchema):
    streamId = ma.fields.String(
        data_key='stream_id',
        dump_only=True,
        description='Identifier of the stream')
    createdAt = Timestamp(
        data_key='created_at',
        dump_only=True,
        description='Time when the subscription was established')


class ConnectionSchema(BaseSchema):
    id = ma.fields.String(
        dump_only=True,
        description='Identifier of the Connection')
    data = ma.fields.String(
        load_only=True,
        description='Metadata associated to this Connection. This populates property `server_data` of the Connection object')
    status = ma.fields.String(
        dump_only=True,
        validate=OneOf(['pending', 'active']),
        description='Status of the Connection')
    sessionId = SessionId(
        data_key='session_id',
        dump_only=True,
        description='Identifier of the Session to which the user is connected')
    createdAt = Timestamp(
        data_key='created_at',
        dump_only=True,
        description='Time when the connection was created')
    activeAt = Timestamp(
        data_key='active_at',
        dump_only=True,
        allow_none=True,
        description='Time when the Connection was taken by a user by calling method Session.connect with the Connection\'s token property')
    platform = ma.fields.String(
        dump_only=True,
        allow_none=True,
        description='Complete description of the platform used by the participant to connect to the Session')
    token = ma.fields.String(
        dump_only=True,
        description='Token of the Connection')
    serverData = ma.fields.String(
        data_key='server_data',
        dump_only=True,
        description='Data assigned to the Connection in your application\'s server-side when creating the Connection')
    clientData = ma.fields.String(
        data_key='client_data',
        dump_only=True,
        allow_none=True,
        description='Data assigned to the Connection in your application\'s client-side when calling Session.connect')


class KurentoOptionsSchema(StreamsConfigSchema):
    allowedFilters = ma.fields.List(
        ma.fields.String,
        data_key='allowed_filters',
        description='Names of the filters the Connection will be able to apply to its published streams')


class WebRtcConnectionSchema(ConnectionSchema):
    role = ma.fields.String(
        validate=OneOf(['SUBSCRIBER', 'PUBLISHER', 'MODERATOR']),
        missing='PUBLISHER',
        description='Defines the role of the Connection')
    publishers = ma.fields.List(
        ma.fields.Nested(PublisherSchema),
        dump_only=True,
        allow_none=True,
        description='Streams the Connection is currently publishing')
    subscribers = ma.fields.List(
        ma.fields.Nested(SubscriberSchema),
        dump_only=True,
        allow_none=True,
        description='Streams the user is currently subscribed to')
    kurentoOptions = ma.fields.Nested(
        KurentoOptionsSchema,
        allow_none=True,
        data_key='kurento_options',
        description='Configuration properties for the Connection regarding Kurento')


class SessionSchema(BaseSchema):
    id = ma.fields.String(
        dump_only=True,
        description='Identifier of the session')
    createdAt = Timestamp(
        data_key='created_at',
        dump_only=True,
        description='Time when the session was created')
    mediaMode = ma.fields.String(
        data_key='media_mode',
        validate=OneOf(['ROUTED', 'RELAYED']),
        missing='ROUTED',
        description='Media mode configured for the session')
    recordingMode = ma.fields.String(
        data_key='recording_mode',
        validate=OneOf(['MANUAL', 'ALWAYS']),
        missing='MANUAL',
        description='Recording mode configured for the session')
    defaultRecordingProperties = ma.fields.Nested(
        DefaultRecordingPropertiesSchema,
        missing=None,
        data_key='default_recording_properties',
        description='The recording properties to apply by default to any recording started for this Session')
    customSessionId = String(
        data_key='custom_session_id',
        missing=None,
        description='Custom session identifier')
    connections = List(
        ma.fields.Nested(WebRtcConnectionSchema),
        data_key='active_connections',
        dump_only=True,
        description='Collection of active connections in the session')
    recording = ma.fields.Boolean(
        dump_only=True,
        description='Whether the session is being recorded or not at this moment')
    forcedVideoCodec = ma.fields.String(
        data_key='forced_media_codec',
        validate=OneOf(['VP8', 'H264', 'NONE']),
        missing='VP8',
        description='Ensure that all the browsers use the same codec, avoiding transcoding process in '
        'the media server, which result in a reduce of CPU usage.')
    allowTranscoding = ma.fields.Boolean(
        data_key='allow_transcoding',
        missing=False,
        description='Defines if transcoding is allowed or not when forcedVideoCodec is not a compatible '
        'codec with the browser')


class SignalSchema(BaseSchema):
    to = ma.fields.List(
        ma.fields.String,
        description='List of connection identifiers to which to send the signal. If this property is not included '
        'or is an empty array, the signal will be sent to all participants of the session')
    type = ma.fields.String(
        description='Type of the signal')
    data = ma.fields.String(
        description='Actual data of the signal')
