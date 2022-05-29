//home.html
function copyToClipboard(item) {
    navigator.clipboard.writeText(item.title);
}

//profile.html
function localeOnChange(lang_options) {
    var selLocale = document.getElementById('search_locale')
    var selGender = document.getElementById('search_gender')
    var selVoice = document.getElementById('search_voice')
    selVoice.length = 1;
    selGender.length = 1;
    for (var y in lang_options[selLocale.value]) {
        selGender.options[selGender.options.length] = new Option(y, y);
    }
}
function genderOnChange(lang_options) {
    var selLocale = document.getElementById('search_locale')
    var selGender = document.getElementById('search_gender')
    var selVoice = document.getElementById('search_voice')
    selVoice.length = 1;
    var z = lang_options[selLocale.value][selGender.value];
    for (var i = 0; i < z.length; i++) {
        selVoice.options[selVoice.options.length] = new Option(z[i], z[i]);
    }
}
function showSpeedVal(value){
    document.getElementById('speedvalue').innerHTML = value;
}
function showPitchVal(value){
    document.getElementById('pitchvalue').innerHTML = value;
}
function editAlias() {
    alias = document.getElementsByName('editPreferredName')[0]
    if (alias.disabled == true) {
        alias.value = ""
        alias.disabled = false
    }
}

function playIntelligent(src) {
    alias = document.getElementsByName('editPreferredName')[0]
    var regex = /(name=)(.*)(&email)/g;
    var result = src;
    if (alias.value != "") {
        result = src.replace(regex, `$1` + alias.value + `$3`);
    }
    toggleAudioControl(true, false);
    var audio = document.querySelector('audio#record');
    audio.src = result;
    audio.play();
}

function playStandard(name) {
    var voice = document.getElementById('search_voice');
    var speed = document.getElementById('speedvalue');
    var pitch = document.getElementById('pitchvalue');
    if(voice.value != '') {
        var audio = document.querySelector('audio#standard');
        var nm = name;
        alias = document.getElementsByName('editPreferredName')[0]
        if (alias.value != "") {
            nm = alias.value;
        }
        audio.src = "/api/standard/pronounce?name='" + nm + "'&voice=" + voice.value + "&pitch=" + parseFloat(pitch.innerHTML) + "&speed=" + parseFloat(speed.innerHTML);
        audio.play();
    } else {
        alert("Select a voice")
    }
}

var recorder;
var recordingBlob = new Blob();
function toggleRecording(chkbox) {
    window.URL = window.URL || window.webkitURL;
    navigator.getUserMedia  = navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia || navigator.msGetUserMedia;
    window.AudioContext = window.AudioContext || window.webkitAudioContext;
    var audio = document.querySelector('audio#record');

    var onFail = function(e) {
        console.log('Rejected!', e);
    };

    var onSuccess = function(stream) {
        var context = new AudioContext();
        var mediaStreamSource = context.createMediaStreamSource(stream);
        recorder = new Recorder(mediaStreamSource, {numChannels:1});
        recorder.record();
    }

    if (chkbox.checked == true) {
        //Recording starts
        if (navigator.getUserMedia) {
            navigator.getUserMedia({audio: true, video: false}, onSuccess, onFail);
        } else {
            console.log('navigator.getUserMedia not present');
        }
        toggleAudioControl(false, chkbox.checked);
    } else {
        //Recording stopped
        var url;
        recorder.stop();
        recorder.exportWAV(function(stream) {
            recordingBlob = stream;
            url = window.URL.createObjectURL(stream)
            audio.src = url;
        });
        toggleAudioControl(true, chkbox.checked);
    }
}

function saveRecording() {
    var alias = document.getElementsByName('editPreferredName')[0];
    var xmlhttp = new XMLHttpRequest();
    var url = "/save_rec/" + alias.value;
    xmlhttp.open("POST", url, true);
    xmlhttp.setRequestHeader("Content-type", "audio/wav");
    xmlhttp.send(recordingBlob);
}

function forbidRecording() {
    document.querySelector('audio#record').src = "";
    toggleAudioControl(false, false);
}

function toggleAudioControl(recording_found, recording_in_progress) {
    if(recording_in_progress == true) {
        document.getElementById('noRecFound').style.display = 'none';
        document.getElementById('recording').style.display = 'block';
        if(recording_found == false) {
            document.getElementById('doneRecording').style.display = 'none';
            document.getElementById('intPlay').style.display = 'block';
            document.getElementById('uploadCustom').style.display = 'none';
        }
    } else if(recording_in_progress == false) {
        document.getElementById('recording').style.display = 'none';
        if(recording_found == true) {
            document.getElementById('noRecFound').style.display = 'none'
            document.getElementById('doneRecording').style.display = 'block';
            document.getElementById('uploadCustom').style.display = 'block';
            document.getElementById('intPlay').style.display = 'none';
        } else {
            document.getElementById('noRecFound').style.display = 'block'
            document.getElementById('doneRecording').style.display = 'none';
            document.getElementById('uploadCustom').style.display = 'none';
            document.getElementById('intPlay').style.display = 'block';
        }
    }
}


function addSaveEmbeddedUrl() {
    if (document.getElementById('nameedit').style.display == 'block') {
        document.getElementById('nameedit').style.display = 'none';
        document.getElementById('namecheck').style.display = 'block';
        document.getElementById('namelbl').style.display = 'none';
        document.getElementById('nametxt').style.display = 'block';
    } else {
        var text = document.getElementById('nametxt').value;
        document.getElementById('namelbl').value = "";
        document.getElementById('namelbl').innerHTML = text;
        document.getElementById('nameedit').style.display = 'block';
        document.getElementById('namecheck').style.display = 'none';
        document.getElementById('namelbl').style.display = 'block';
        document.getElementById('nametxt').style.display = 'none';
    }
}

document.addEventListener('mouseup', event => {
    if(window.getSelection().toString().length){
       let exactText = window.getSelection().toString();
       document.getElementById('selectedText').innerHTML = exactText.trim();
    }
});

function playHighlightText() {
    var text = document.getElementById('selectedText').innerHTML;
    if (text.length) {
        var url = "/api/pronounce?name=" + text;
        var audio = document.querySelector('audio#consoleStandard');
        audio.src = url;
        audio.play();
    } else {
        alert("Highlight a name to pronounce!!")
    }
}

function endPlayingConsole() {
    document.getElementById('selectedText').innerHTML = "";
    if (window.getSelection) {
        if (window.getSelection().empty) {  // Chrome
        window.getSelection().empty();
      } else if (window.getSelection().removeAllRanges) {  // Firefox
            window.getSelection().removeAllRanges();
      }
    } else if (document.selection) {  // IE?
            document.selection.empty();
    }
}
