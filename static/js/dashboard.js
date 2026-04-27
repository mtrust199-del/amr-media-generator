// dashboard.js – AMR OMNI Command Center frontend logic

// Clock update
function updateClock() {
  const now = new Date();
  document.getElementById('system-clock').textContent = now.toLocaleTimeString();
}
setInterval(updateClock, 1000);
updateClock();

// Progress overlay helpers
function showProgress(title) {
  document.getElementById('progress-title').textContent = title;
  document.getElementById('progress-fill').style.width = '0%';
  document.getElementById('progress-log').innerHTML = '';
  document.getElementById('progress-overlay').classList.add('active');
}

function updateProgress(pct, message) {
  document.getElementById('progress-fill').style.width = pct + '%';
  if (message) {
    const log = document.getElementById('progress-log');
    log.innerHTML += '<div>' + new Date().toLocaleTimeString() + ' ' + message + '</div>';
    log.scrollTop = log.scrollHeight;
  }
}

function hideProgress() {
  document.getElementById('progress-overlay').classList.remove('active');
}

document.getElementById('close-progress').addEventListener('click', hideProgress);

// Open folder actions
document.getElementById('open-root').addEventListener('click', () => {
  fetch('/open-folder?path=root', {method: 'POST'})
    .then(r => r.json())
    .then(data => alert(data.message || 'Folder opened'));
});

document.getElementById('open-media').addEventListener('click', () => {
  fetch('/open-folder?path=media', {method: 'POST'})
    .then(r => r.json())
    .then(data => alert(data.message || 'Folder opened'));
});

// Autonomous Auth Test
document.getElementById('auth-test').addEventListener('click', () => {
  showProgress('Autonomous Auth Test');
  updateProgress(10, 'Starting Playwright...');

  fetch('/auth/test', {method: 'POST'})
    .then(r => r.json())
    .then(data => {
      updateProgress(100, data.success ? 'Success': 'Failed: ' + (data.error || 'Unknown'));
    })
    .catch(err => {
      updateProgress(100, 'Error: ' + err.message);
    });
});

// Status LED pulse animation
function setStatus(module, active) {
  const card = document.getElementById('status-' + module);
  if (!card) return;
  const led = card.querySelector('.status-led');
  const info = card.querySelector('.status-info p');
  if (active) {
    led.className = 'status-led active';
    info.textContent = 'Active';
  } else {
    led.className = 'status-led inactive';
    info.textContent = 'Idle';
  }
}

// Poll backend for status
function pollStatus() {
  fetch('/api/status')
    .then(r => r.json())
    .then(data => {
      setStatus('playwright', data.playwright);
      setStatus('sync', data.sync);
      setStatus('github', data.github);
      setStatus('n8n', data.n8n);
    })
    .catch(() => {});
}
setInterval(pollStatus, 5000);
pollStatus();
