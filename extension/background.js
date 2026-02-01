/**
 * Background Service Worker
 * Handles extension lifecycle and messaging
 */

// Listen for messages from content script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'CAPTURE_SUCCESS') {
    // Show notification on successful capture
    chrome.notifications.create({
      type: 'basic',
      iconUrl: 'icons/icon48.png',
      title: 'AI Study Assistant',
      message: `Saved to ${message.data.topic}`,
      priority: 1
    });
  }
});

// Set default API URL on install
chrome.runtime.onInstalled.addListener(() => {
  chrome.storage.sync.get('apiUrl', (result) => {
    if (!result.apiUrl) {
      chrome.storage.sync.set({ apiUrl: 'http://localhost:8000' });
    }
  });
});
