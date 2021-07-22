var OV;
var session;

var TRIES = 20;
var TOKEN = null;

var REFRESH_INTERVAL = null;

$.getScript('https://github.com/OpenVidu/openvidu/releases/download/v2.11.0/openvidu-browser-2.11.0.min.js', function () {
    OV = new OpenVidu();
    session = OV.initSession();

	session.on("streamCreated", function (event) {
		session.subscribe(event.stream, "subscribers");
	});

    REFRESH_INTERVAL = setInterval(() => {
        const token = document.getElementById("openvidu-token").value;
        console.log("Waiting for openvidu token...");
        if (token) {
            clearInterval(REFRESH_INTERVAL);
            initVideo(token);
            console.log(token);
        }
    }, 500);
});

async function initVideo(token) {
    console.log("Initializing openvidu...");

    await session.connect(token);

    const publisher = OV.initPublisher("publisher");
    session.publish(publisher);
}

socket.on("command", (data) => {
    console.log(data)
});