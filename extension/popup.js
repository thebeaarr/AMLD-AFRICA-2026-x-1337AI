/**
 * Popup Script - Extension settings and stats
 */

const apiUrlInput = document.getElementById('apiUrl');
const saveBtn = document.getElementById('saveBtn');
const statusMsg = document.getElementById('statusMsg');
const captureCountEl = document.getElementById('captureCount');

// Load saved settings
chrome.storage.sync.get(['apiUrl', 'captureCount'], (result) => {
  if (result.apiUrl) {
    apiUrlInput.value = result.apiUrl;
  }
  if (result.captureCount) {
    captureCountEl.textContent = result.captureCount;
  }
});

// Save settings
saveBtn.addEventListener('click', () => {
  const apiUrl = apiUrlInput.value.trim();
  
  if (!apiUrl) {
    showStatus('Please enter an API URL', 'error');
    return;
  }

  // Validate URL format
  try {
    new URL(apiUrl);
  } catch (e) {
    showStatus('Invalid URL format', 'error');
    return;
  }

  // Save to storage
  chrome.storage.sync.set({ apiUrl }, () => {
    showStatus('Settings saved successfully!', 'success');
  });
});

// Show status message
function showStatus(message, type) {
  statusMsg.textContent = message;
  statusMsg.className = `text-sm text-center py-2 rounded-md ${
    type === 'success' 
      ? 'bg-green-100 text-green-800' 
      : 'bg-red-100 text-red-800'
  }`;
  statusMsg.classList.remove('hidden');
  
  setTimeout(() => {
    statusMsg.classList.add('hidden');
  }, 3000);
}

// Listen for capture events to update count
chrome.runtime.onMessage.addListener((message) => {
  if (message.type === 'CAPTURE_SUCCESS') {
    chrome.storage.sync.get('captureCount', (result) => {
      const count = (result.captureCount || 0) + 1;
      chrome.storage.sync.set({ captureCount: count });
      captureCountEl.textContent = count;
    });
  }
});

// Test connection button functionality
apiUrlInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') {
    saveBtn.click();
  }
});
