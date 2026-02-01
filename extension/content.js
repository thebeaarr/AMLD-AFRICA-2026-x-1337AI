/**
 * Content Script - Runs on all web pages
 * Detects text selection and shows a "Capture" button
 */

let captureButton = null;
let selectedText = '';

// Create the capture button
function createCaptureButton() {
  const button = document.createElement('div');
  button.id = 'ai-study-capture-btn';
  button.innerHTML = `
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>
      <polyline points="17 21 17 13 7 13 7 21"/>
      <polyline points="7 3 7 8 15 8"/>
    </svg>
    <span>Capture</span>
  `;
  button.className = 'ai-study-capture-button';
  button.style.display = 'none';
  document.body.appendChild(button);
  return button;
}

// Position button near the selected text
function positionButton(selection) {
  if (!captureButton) return;
  
  const range = selection.getRangeAt(0);
  const rect = range.getBoundingClientRect();
  
  // Position button at top-right of selection
  const top = rect.top + window.scrollY - 40;
  const left = rect.left + window.scrollX + (rect.width / 2) - 50;
  
  captureButton.style.top = `${top}px`;
  captureButton.style.left = `${left}px`;
  captureButton.style.display = 'flex';
}

// Hide the button
function hideButton() {
  if (captureButton) {
    captureButton.style.display = 'none';
  }
}

// Handle text selection
function handleSelection() {
  const selection = window.getSelection();
  const text = selection.toString().trim();
  
  if (text.length > 10) {
    selectedText = text;
    positionButton(selection);
  } else {
    hideButton();
  }
}

// Send captured text to backend
async function captureText() {
  if (!selectedText) return;
  
  // Show loading state
  captureButton.innerHTML = `
    <svg class="animate-spin" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <circle cx="12" cy="12" r="10" stroke-opacity="0.25"/>
      <path d="M12 2a10 10 0 0 1 10 10" stroke-opacity="0.75"/>
    </svg>
    <span>Saving...</span>
  `;
  captureButton.classList.add('loading');
  
  try {
    // Get API URL from storage
    const { apiUrl = 'http://localhost:8000' } = await chrome.storage.sync.get('apiUrl');
    
    // Send to backend
    const response = await fetch(`${apiUrl}/capture`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text: selectedText,
        url: window.location.href,
        pageTitle: document.title
      })
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    
    const data = await response.json();
    
    // Show success state
    captureButton.innerHTML = `
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
        <polyline points="22 4 12 14.01 9 11.01"/>
      </svg>
      <span>Saved!</span>
    `;
    captureButton.classList.remove('loading');
    captureButton.classList.add('success');
    
    // Send notification
    chrome.runtime.sendMessage({
      type: 'CAPTURE_SUCCESS',
      data: data.data
    });
    
    // Reset button after showing success
    setTimeout(() => {
      captureButton.innerHTML = `
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>
          <polyline points="17 21 17 13 7 13 7 21"/>
          <polyline points="7 3 7 8 15 8"/>
        </svg>
        <span>Capture</span>
      `;
      captureButton.classList.remove('success');
      hideButton();
      // Don't clear selection - let user select again if they want
    }, 1500);
    
  } catch (error) {
    console.error('Capture error:', error);
    
    // Show error state
    captureButton.innerHTML = `
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10"/>
        <line x1="15" y1="9" x2="9" y2="15"/>
        <line x1="9" y1="9" x2="15" y2="15"/>
      </svg>
      <span>Error</span>
    `;
    captureButton.classList.remove('loading');
    captureButton.classList.add('error');
    
    // Reset after 2 seconds
    setTimeout(() => {
      captureButton.innerHTML = `
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>
          <polyline points="17 21 17 13 7 13 7 21"/>
          <polyline points="7 3 7 8 15 8"/>
        </svg>
        <span>Capture</span>
      `;
      captureButton.classList.remove('error');
    }, 2000);
  }
}

// Initialize
function init() {
  captureButton = createCaptureButton();
  
  // Listen for text selection
  document.addEventListener('mouseup', () => {
    setTimeout(handleSelection, 10);
  });
  
  document.addEventListener('selectionchange', () => {
    const selection = window.getSelection();
    if (selection.isCollapsed) {
      hideButton();
    }
  });
  
  // Handle button click
  captureButton.addEventListener('click', (e) => {
    e.stopPropagation();
    captureText();
  });
  
  // Hide button when clicking elsewhere
  document.addEventListener('mousedown', (e) => {
    if (e.target !== captureButton && !captureButton.contains(e.target)) {
      const selection = window.getSelection();
      if (selection.isCollapsed) {
        hideButton();
      }
    }
  });
}

// Start when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
