//webkitURL is deprecated but nevertheless
URL = window.URL || window.webkitURL;

var gumStream; 						//stream from getUserMedia()
var rec; 							//Recorder.js object
var input; 							//MediaStreamAudioSourceNode we'll be recording

// shim for AudioContext when it's not avb. 
var AudioContext = window.AudioContext || window.webkitAudioContext;
var audioContext //audio context to help us record

var recordButton = document.getElementById("recordButton");
var stopButton = document.getElementById("stopButton");

//add events to those 2 buttons
recordButton.addEventListener("click", startRecording);
stopButton.addEventListener("click", stopRecording);

var clickedStart
var clickedStop

var reqs = []

function startRecording() {
	reqs = [];
	$("#flag").attr('src', "static/images/none.png");

	$("#croatian").html('0.0000')
	$("#french").html('0.0000')
	$("#spanish").html('0.0000')

	$("#transcription").html('')
	$("#translation").html('')

	var audioPlayer = $("#audio_player");
	$("#output_speech").attr('src', " ")
	audioPlayer[0].pause()
	audioPlayer[0].load()


	/*
		Simple constraints object, for more advanced audio features see
		https://addpipe.com/blog/audio-constraints-getusermedia/
	*/
    
    var constraints = { audio: true, video:false }

 	/*
    	Disable the record button until we get a success or fail from getUserMedia() 
	*/

	recordButton.disabled = true;
	stopButton.disabled = false;

	/*
    	We're using the standard promise based getUserMedia() 
    	https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia
	*/

	navigator.mediaDevices.getUserMedia(constraints).then(function(stream) {
		console.log("getUserMedia() success, stream created, initializing Recorder.js ...");

		/*
			create an audio context after getUserMedia is called
			sampleRate might change after getUserMedia is called, like it does on macOS when recording through AirPods
			the sampleRate defaults to the one set in your OS for your playback device
		*/
		audioContext = new AudioContext();

		//update the format 
		document.getElementById("formats").innerHTML="Format: 1 channel pcm @ "+audioContext.sampleRate/1000+"kHz"

		/*  assign to gumStream for later use  */
		gumStream = stream;
		
		/* use the stream */
		input = audioContext.createMediaStreamSource(stream);

		/* 
			Create the Recorder object and configure to record mono sound (1 channel)
			Recording 2 channels  will double the file size
		*/
		rec = new Recorder(input,{numChannels:1})

		//start the recording process
		rec.record()

		console.log("Recording started");

	}).catch(function(err) {
	  	//enable the record button if getUserMedia() fails
    	recordButton.disabled = false;
    	stopButton.disabled = true;
	});
}



async function stopRecording() {
	//disable the stop button, enable the record too allow for new recordings
	stopButton.disabled = true;

	//tell the recorder to stop the recording
	rec.stop();

	//stop microphone access
	gumStream.getAudioTracks()[0].stop();

	//create the wav blob and pass it on to createDownloadLink
	rec.exportWAV(sendData); // createDownloadLink

	// waits for all requests to finish before enabling the recordButton again
	waitForRequestsToBeDone()
}

function waitForRequestsToBeDone() {
		if(reqs.length < 4) {//we want it to match
			setTimeout(waitForRequestsToBeDone, 50);//wait 50 millisecnds then recheck
			return;
		}
		recordButton.disabled = false
	}

function sendData(blob) {
	var xhr = new XMLHttpRequest();
    xhr.open("POST", "/", true);
    xhr.setRequestHeader("content-type", "audio/wav");
    xhr.onload = function(e) {
		all_requests()
    }
    xhr.send(blob);
}

function all_requests(){
	var req = $.get({
		url:"/get_flag_and_probs", 
		cache: false,
		success: function(result){
			$("#flag").attr('src', result.flag);
			probabilites = result.probabilities
			probabilites = probabilites.split(' ')
			$("#croatian").html(probabilites[0])
			$("#french").html(probabilites[1])
			$("#spanish").html(probabilites[2])
			}
		}
	)
	.done(function(){
		reqs.push(req)
		req = $.get({
			url:"/get_transcription", 
			cache: false,
			success: function(result){
				$("#transcription").html(result.transcription)
			}
		})
		.done(function(){
			reqs.push(req)
			req = $.get({
				url:"/get_translation", 
				cache: false,
				success: function(result){
					$("#translation").html(result.translation)
				}
			})
			.done(function(){
				reqs.push(req)
				req = $.get({
					url:"/get_output_speech", 
					cache: false,
					success: function(result){
						var audioPlayer = $("#audio_player");
						$("#output_speech").attr('src', result.output_speech)
						audioPlayer[0].pause()
						audioPlayer[0].load()
						audioPlayer[0].oncanplaythrough = audioPlayer[0].play();
					}
				});
			})
			reqs.push(req)
		})
	})
	
}