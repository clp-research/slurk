var OV;
var session;

var TRIES = 20;
var TOKEN = null;

var REFRESH_INTERVAL = null;

$(document).ready(() => {
    OV = new OpenVidu();
    session = OV.initSession();

	session.on("streamCreated", function (event) {
		session.subscribe(event.stream, "subscribers");
	});

    console.log("script");

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