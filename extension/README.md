# AI Study Assistant - Chrome Extension

A Chrome extension that lets you capture highlighted text with AI-powered summarization and save it to Notion.

## ✨ Features

- **📝 Quick Capture**: Highlight any text on a webpage, click "Capture" button
- **🤖 AI Summary**: Automatically summarizes content into bullet points
- **🏷️ Smart Categorization**: Classifies by subject and topic
- **💾 Notion Integration**: Saves directly to your Notion database
- **🎨 Tailwind UI**: Beautiful popup interface with settings
- **📊 Stats Tracking**: See how many notes you've captured

## 🚀 Installation

### 1. Load Extension in Chrome

1. Open Chrome and go to `chrome://extensions/`
2. Enable **Developer mode** (toggle in top-right)
3. Click **Load unpacked**
4. Select the `extension` folder from this project

### 2. Configure Backend

1. Make sure your FastAPI backend is running:
   ```bash
   cd ../backend
   python main.py
   ```

2. Click the extension icon in Chrome
3. Enter your backend URL (default: `http://localhost:8000`)
4. Click **Save Settings**

## 📖 How to Use

1. **Highlight text** on any webpage (at least 10 characters)
2. A **"Capture" button** appears near your selection
3. Click it to send the text to AI for processing
4. Get a notification when saved to Notion!

## 📁 Extension Structure

```
extension/
├── manifest.json        # Extension configuration
├── content.js          # Runs on web pages, handles text selection
├── background.js       # Service worker for notifications
├── popup.html          # Settings popup (Tailwind styled)
├── popup.js            # Popup functionality
├── styles/
│   └── content.css     # Capture button styles
└── icons/
    ├── icon16.png
    ├── icon48.png
    └── icon128.png
```

## 🎯 How It Works

1. **Content Script** (`content.js`) detects text selection
2. **Capture Button** appears near highlighted text
3. On click, sends data to backend API:
   ```json
   {
     "text": "highlighted text",
     "url": "https://current-page.com",
     "pageTitle": "Page Title"
   }
   ```
4. **Backend processes** with AI and saves to Notion
5. **Notification** shows success/error

## ⚙️ Settings

Access settings by clicking the extension icon:

- **Backend API URL**: Your FastAPI server URL
- **Capture Stats**: See daily capture count

## 🎨 Customization

### Change Button Appearance

Edit [styles/content.css](styles/content.css):
```css
.ai-study-capture-button {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  /* Your custom styles */
}
```

### Change Popup Design

Edit [popup.html](popup.html) - uses Tailwind CSS classes

### Modify Icon

Replace icons in `icons/` folder (16x16, 48x48, 128x128 PNG)

## 🔧 Development

### Test Changes

1. Make your code changes
2. Go to `chrome://extensions/`
3. Click the **refresh icon** on your extension card
4. Test on any webpage

### Debug

- **Content Script**: Right-click page → Inspect → Console
- **Popup**: Right-click extension icon → Inspect popup
- **Background**: chrome://extensions/ → Service worker → Inspect

## 📝 Permissions

- `activeTab`: Access current tab's content
- `storage`: Save settings and stats
- `host_permissions`: Send requests to backend API

## 🐛 Troubleshooting

**Button doesn't appear:**
- Ensure you highlighted >10 characters
- Check console for errors (F12)

**Capture fails:**
- Verify backend is running on port 8000
- Check API URL in extension settings
- Look at Network tab in DevTools

**CORS error:**
- Backend already has CORS enabled for all origins
- Make sure backend is running

## 🚀 Next Steps

- Add keyboard shortcut (Ctrl+Shift+S)
- Offline queue for captures
- Rich text formatting support
- Custom categories in popup
- Export notes feature

## 📄 License

MIT License - Perfect for hackathons!

---

Built with 💜 using Chrome Extensions API + Tailwind CSS
