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
	
	reqs = []; // basically resets the number of requests 
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
	document.getElementById("formats").innerHTML="Format: start recording to see sample rate"
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
		// 3 is the number of requests in the function transcription_translation_speech()
		// It waits for them all to be done in order to let the user use the functionality again
		if(reqs.length < 3) { 
			setTimeout(waitForRequestsToBeDone, 50); //wait 50 milliseconds then recheck
			return;
		}
		recordButton.disabled = false
	}

function sendData(blob) {
	// Function that sends the audio to the backend and receives the response
	// that contains the path (filename) of the audio, detected language,
	// path to the flag img for the detected language, and the probabilites of its confidence 
	var xhr = new XMLHttpRequest();
    xhr.open("POST", "/", true);
    xhr.setRequestHeader("content-type", "audio/wav");
    xhr.onload = function(e) {
		var response = JSON.parse(xhr.response)
		show_flag_probs(response.flag, response.probabilities)
		transcription_translation_speech(response.filename, response.detected_lang)
	}
    xhr.send(blob);
}


function show_flag_probs(flag, probabilities){
	$("#flag").attr('src', flag);
	probabilities = probabilities.split(' ')
	$("#croatian").html(probabilities[0])
	$("#french").html(probabilities[1])
	$("#spanish").html(probabilities[2])
}

function transcription_translation_speech(filename, detected_lang){
	var transcription
	var translation

	var req = $.get({
			url:"/get_transcription",
			data: {
				filename: filename,
				detected_lang: detected_lang
			}, 
			cache: false,
			success: function(result){
				transcription = result.transcription
				$("#transcription").html(transcription)
			}
		})
		.done(function(){
			reqs.push(req) // for counting the number of requests afterwards in the waitForRequestsToBeDone()
			req = $.get({
				url:"/get_translation", 
				data: {
					transcription: transcription
				},
				cache: false,
				success: function(result){
					translation = result.translation
					$("#translation").html(translation)
				}
			})
			.done(function(){
				reqs.push(req) // for counting the number of requests afterwards in the waitForRequestsToBeDone()
				req = $.get({
					url:"/get_output_speech", 
					data: {
						translation: translation
					},
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
			reqs.push(req) // for counting the number of requests afterwards in the waitForRequestsToBeDone()
		})
	}