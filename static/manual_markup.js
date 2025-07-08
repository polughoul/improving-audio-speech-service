let wavesurfer = WaveSurfer.create({
    container: '#waveform',
    waveColor: '#4f8cff',
    progressColor: '#2563eb',
    height: 90,
    responsive: true,
    backend: 'MediaElement'
});

wavesurfer.load('/static/sounds/beep.wav'); 

let segments = [];
let regionStart = null;

wavesurfer.on('seek', () => {
    regionStart = wavesurfer.getCurrentTime();
});

document.getElementById('add-segment-btn').onclick = function() {
    let end = wavesurfer.getCurrentTime();
    if (regionStart !== null && end > regionStart) {
        segments.push({start: regionStart, end: end});
        updateSegmentsList();
    }
    regionStart = null;
};

document.getElementById('clear-segments-btn').onclick = function() {
    segments = [];
    updateSegmentsList();
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

document.getElementById('manual-censor-btn').onclick = function() {
    alert('todo');
};