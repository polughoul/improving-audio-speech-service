document.querySelector('input[type="file"]')?.addEventListener('change', function(e) {
    const fileName = e.target.files[0]?.name || "Download file";
    document.getElementById('file-upload-text').textContent = fileName;
});

document.getElementById('select-all-btn')?.addEventListener('click', function() {
    document.querySelectorAll('#marks-list input[type="checkbox"]').forEach(cb => cb.checked = true);
});

document.getElementById('action')?.addEventListener('change', function() {
    document.getElementById('funny-sound-select').style.display =
        this.value === 'funny' ? 'block' : 'none';
});


function showSpinner() {
    document.getElementById('loading-spinner').style.display = 'flex';
}

document.getElementById('badwords-form')?.addEventListener('submit', function() {
    showSpinner();
});
document.getElementById('marks-form')?.addEventListener('submit', function() {
    showSpinner();
});