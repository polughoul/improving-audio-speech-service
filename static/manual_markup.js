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

document.getElementById('manual-audio-file').addEventListener('change', async function(e) {
    const file = e.target.files[0];
    if (file) {
        showSpinner();
        const url = URL.createObjectURL(file);
        document.getElementById('manual-file-upload-text').textContent = file.name;
        segments = [];
        clearRegions();
        updateSegmentsList();

        const formData = new FormData();
        formData.append('audio', file);
        const resp = await fetch('/diarize', {
            method: 'POST',
            body: formData
        });
        let speakers = null;
        let speaker_files = null;
        if (resp.ok) {
            const data = await resp.json();
            speakers = data.speakers;
            speaker_files = data.speaker_files;
        }

        const respBad = await fetch('/detect-badwords', {
            method: 'POST',
            body: formData
        });
        let badwords = [];
        if (respBad.ok) {
            const data = await respBad.json();
            badwords = data.marks || [];
        }

        const container = document.getElementById('speaker-waveforms');
        container.innerHTML = '';

        if (speakers && Object.keys(speakers).length > 1 && speaker_files) {
            document.getElementById('waveform').style.display = 'none';
            document.getElementById('play-btn').style.display = 'none';
            document.getElementById('add-segment-btn').style.display = '';
            document.getElementById('clear-segments-btn').style.display = '';
            document.getElementById('segments-list').style.display = '';

            let html = '';
            Object.keys(speakers).forEach((spk, idx) => {
                const wfId = `waveform-speaker-${idx}`;
                html += `
                    <div style="margin:18px 0;">
                        <b>Speaker ${spk}</b>
                        <div id="${wfId}" style="height:90px;"></div>
                        <div style="margin-top:8px;">
                            <button id="play-btn-${wfId}" type="button">Play/Pause</button>
                            <label style="margin-left:12px;">Speed:
                                <select id="speed-${wfId}">
                                    <option value="0.5">0.5x</option>
                                    <option value="0.75">0.75x</option>
                                    <option value="1" selected>1x</option>
                                    <option value="1.25">1.25x</option>
                                    <option value="1.5">1.5x</option>
                                    <option value="2">2x</option>
                                </select>
                            </label>
                            <label style="margin-left:12px;">Volume:
                                <input id="volume-${wfId}" type="range" min="0" max="1" step="0.01" value="1" style="width:80px;">
                            </label>
                        </div>
                    </div>`;
            });
            container.innerHTML = html;

            Object.keys(speakers).forEach((spk, idx) => {
                const wfId = `waveform-speaker-${idx}`;
                let ws = WaveSurfer.create({
                    container: `#${wfId}`,
                    waveColor: ['#4f8cff', '#2563eb', '#2ecc40'][idx % 3],
                    progressColor: '#2563eb',
                    height: 90,
                    responsive: true,
                    backend: 'MediaElement',
                    plugins: [
                        WaveSurfer.regions.create()
                    ]
                });
                const spkFileName = speaker_files[spk].split(/[\\/]/).pop();
                ws.load(`/uploads/${spkFileName}`);
                badwords.forEach(mark => {
                    ws.addRegion({
                        start: mark.start,
                        end: mark.end,
                        color: 'rgba(255,0,0,0.3)',
                        drag: false,
                        resize: false
                    });
                });
                setTimeout(() => {
                    document.getElementById(`play-btn-${wfId}`).onclick = () => ws.playPause();
                    document.getElementById(`speed-${wfId}`).onchange = function() {
                        ws.setPlaybackRate(parseFloat(this.value));
                    };
                    document.getElementById(`volume-${wfId}`).oninput = function() {
                        ws.setVolume(parseFloat(this.value));
                    };
                }, 500);
            });
        } else {
            document.getElementById('waveform').style.display = '';
            document.getElementById('play-btn').style.display = '';
            document.getElementById('add-segment-btn').style.display = '';
            document.getElementById('clear-segments-btn').style.display = '';
            document.getElementById('segments-list').style.display = '';
            container.innerHTML = '';
            wavesurfer.load(url);
            badwords.forEach(mark => {
                addRegion(mark.start, mark.end, 'rgba(255,0,0,0.3)', true);
            });
        }
        hideSpinner();
    }
});

document.getElementById('play-btn').onclick = function() {
    wavesurfer.playPause();
};

document.getElementById('speed-main').onchange = function() {
    wavesurfer.setPlaybackRate(parseFloat(this.value));
};
document.getElementById('volume-main').oninput = function() {
    wavesurfer.setVolume(parseFloat(this.value));
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
            document.getElementById('manual-download-link').innerHTML = ''; 
        }
        regionStart = null;
        this.textContent = "Add Segment";
    }
};

function addRegion(start, end, color='rgba(79,140,255,0.2)', notDraggable=false) {
    let region = wavesurfer.addRegion({
        start: start,
        end: end,
        color: color,
        drag: false,    
        resize: false    
    });
    if (notDraggable) {
        region.element.classList.add('auto-region');
        region.resize = false;
    }
    return region;
}
function clearRegions() {
    Object.values(wavesurfer.regions.list).forEach(region => {
        if (!region.element.classList.contains('auto-region')) {
            region.remove();
        }
    });
}

document.getElementById('clear-segments-btn').onclick = function() {
    segments = [];
    clearRegions();
    updateSegmentsList();
    regionStart = null;
    document.getElementById('add-segment-btn').textContent = "Add Segment";
    document.getElementById('manual-download-link').innerHTML = ''; 
};

function updateSegmentsList() {
    const list = document.getElementById('segments-list');
    list.innerHTML = segments.map((s, i) =>
        `<div style="display:flex;align-items:center;gap:8px;">
            Segment ${i+1}: ${s.start.toFixed(2)} - ${s.end.toFixed(2)} sec
            <span class="delete-segment" data-idx="${i}" style="cursor:pointer;">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                    <path stroke="#e53e3e" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
                        d="M6 6l12 12M6 18L18 6"/>
                </svg>
            </span>
        </div>`
    ).join('');
    document.getElementById('manual-download-link').innerHTML = ''; // очищаем превью
    document.querySelectorAll('.delete-segment').forEach(el => {
        el.onclick = function() {
            const idx = parseInt(this.dataset.idx);
            const seg = segments[idx];
            Object.values(wavesurfer.regions.list).forEach(region => {
                if (Math.abs(region.start - seg.start) < 0.01 && Math.abs(region.end - seg.end) < 0.01 && !region.element.classList.contains('auto-region')) {
                    region.remove();
                }
            });
            segments.splice(idx, 1);
            updateSegmentsList();
        };
    });
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
            `<div class="audio-download-block" style="display:flex;flex-direction:column;align-items:center;gap:18px;">
                <audio controls style="margin-top:18px;">
                    <source src="${data.download_url}" type="audio/wav">
                    Your browser does not support the audio element.
                </audio>
                <a href="${data.download_url}" class="download-btn" download>Download censored file</a>
            </div>`;
    } else {
        alert('Error processing audio');
    }
    document.getElementById('manual-censor-btn').disabled = false;
    document.getElementById('manual-censor-btn').textContent = 'Censor Selected Segments';
};

function showSpinner() {
    document.getElementById('loading-spinner').style.display = 'flex';
}
function hideSpinner() {
    document.getElementById('loading-spinner').style.display = 'none';
}

document.getElementById('waveform').addEventListener('wheel', function(e) {
    e.preventDefault();
    let minPxPerSec = 20;
    let maxPxPerSec = 500;
    let current = wavesurfer.params.minPxPerSec || 100;
    let delta = e.deltaY < 0 ? 20 : -20;
    let next = Math.max(minPxPerSec, Math.min(maxPxPerSec, current + delta));
    wavesurfer.zoom(next);
    wavesurfer.params.minPxPerSec = next;
});

let isDragging = false;
let lastX = 0;
const wf = document.getElementById('waveform');
wf.addEventListener('mousedown', function(e) {
    isDragging = true;
    lastX = e.pageX;
});
window.addEventListener('mousemove', function(e) {
    if (isDragging) {
        wf.scrollLeft -= (e.pageX - lastX);
        lastX = e.pageX;
    }
});
window.addEventListener('mouseup', function() {
    isDragging = false;
});