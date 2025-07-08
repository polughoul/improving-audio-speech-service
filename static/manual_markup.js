let wavesurfer = WaveSurfer.create({
    container: '#waveform',
    waveColor: '#4f8cff',
    progressColor: '#2563eb',
    height: 90,
    responsive: true,
    backend: 'MediaElement',
    plugins: [
        WaveSurfer.regions.create()
    ]
});

document.getElementById('manual-audio-file').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
        const url = URL.createObjectURL(file);
        wavesurfer.load(url);
        document.getElementById('manual-file-upload-text').textContent = file.name;
        segments = [];
        clearRegions();
        updateSegmentsList();
    }
});

document.getElementById('play-btn').onclick = function() {
    wavesurfer.playPause();
};

let segments = [];
let regionStart = null;

document.getElementById('add-segment-btn').onclick = function() {
    if (regionStart === null) {
        regionStart = wavesurfer.getCurrentTime();
        this.textContent = "Set End & Add Segment";
    } else {
        let end = wavesurfer.getCurrentTime();
        if (end > regionStart) {
            segments.push({start: regionStart, end: end});
            addRegion(regionStart, end);
            updateSegmentsList();
        }
        regionStart = null;
        this.textContent = "Add Segment";
    }
};

function addRegion(start, end) {
    wavesurfer.addRegion({
        start: start,
        end: end,
        color: 'rgba(79,140,255,0.2)'
    });
}
function clearRegions() {
    Object.values(wavesurfer.regions.list).forEach(region => region.remove());
}

document.getElementById('clear-segments-btn').onclick = function() {
    segments = [];
    clearRegions();
    updateSegmentsList();
    regionStart = null;
    document.getElementById('add-segment-btn').textContent = "Add Segment";
};

function updateSegmentsList() {
    const list = document.getElementById('segments-list');
    list.innerHTML = segments.map((s, i) =>
        `<div>Segment ${i+1}: ${s.start.toFixed(2)} - ${s.end.toFixed(2)} sec</div>`
    ).join('');
}

document.getElementById('manual-action').onchange = function() {
    document.getElementById('manual-funny-sound').style.display =
        this.value === 'funny' ? 'inline-block' : 'none';
};

document.getElementById('manual-censor-btn').onclick = async function() {
    if (!segments.length) {
        alert('Please add at least one segment!');
        return;
    }
    const action = document.getElementById('manual-action').value;
    const funnySound = document.getElementById('manual-funny-sound').value;
    const fileInput = document.getElementById('manual-audio-file');
    const file = fileInput.files[0];
    if (!file) {
        alert('Please select an audio file!');
        return;
    }

    const formData = new FormData();
    formData.append('audio', file);
    formData.append('segments', JSON.stringify(segments));
    formData.append('action', action);
    formData.append('funny_sound', funnySound);

    document.getElementById('manual-censor-btn').disabled = true;
    document.getElementById('manual-censor-btn').textContent = 'Processing...';

    const resp = await fetch('/manual-markup', {
        method: 'POST',
        body: formData
    });
    if (resp.ok) {
        const data = await resp.json();
        document.getElementById('manual-download-link').innerHTML =
            `<a href="${data.download_url}" class="download-btn" download>Download censored file</a>`;
    } else {
        alert('Error processing audio');
    }
    document.getElementById('manual-censor-btn').disabled = false;
    document.getElementById('manual-censor-btn').textContent = 'Censor Selected Segments';
};