# AI-Powered Student Study Assistant - Chrome Extension

A hackathon demo Chrome extension that captures highlighted text, summarizes it with AI, stores it in SQLite, and optionally syncs to Notion.

## 🎯 What It Does

Highlight text on any webpage → Click "Capture" → AI summarizes → Saved to SQLite → Optional Notion sync ✨

## 🏗️ Architecture

**Primary Storage: SQLite Database**
- All data stored locally in SQLite
- Full control and flexibility
- Fast queries, no API limits
- Relational data integrity

**Optional: Notion Integration**
- Sync notes to Notion for viewing
- Beautiful organization interface
- Can be completely disabled
- Data remains in SQLite either way

## 🏗️ Architecture

```
hackathon/
├── backend/              # FastAPI Server
│   ├── main.py          # API with SQLite database
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
│
└── extension/           # Chrome Extension
    ├── manifest.json    # Extension config
    ├── content.js       # Text selection handler
    ├── background.js    # Service worker
    ├── popup.html       # Settings UI (Tailwind)
    ├── popup.js         # Settings logic
    ├── styles/
    │   └── content.css  # Button styles
    └── icons/
        └── *.png        # Extension icons
```

## 💾 Database Schema

**SQLite Tables:**
- `topics` - Subject categories and topics
- `notes` - Captured highlights with metadata
- `summary_points` - AI-generated bullet points
- `keywords` - Extracted keywords for search

## 🚀 Quick Start

### Backend Setup

1. **Start the FastAPI backend:**
   ```bash
   cd backend
   pip install -r requirements.txt
   python main.py
   ```
   Backend runs on `http://localhost:8000`

### Extension Setup

1. **Load in Chrome:**
   - Open `chrome://extensions/`
   - Enable "Developer mode" (toggle top-right)
   - Click "Load unpacked"
   - Select the `extension` folder

2. **Configure:**
   - Click extension icon in Chrome toolbar
   - Verify API URL: `http://localhost:8000`
   - Click "Save Settings"

## 📖 Usage

1. **Highlight** any text on a webpage (minimum 10 characters)
2. **Click** the "Capture" button that appears next to your selection
3. **Done!** AI processes and saves to Notion
4. Get a notification when complete!

## ✨ Features

### Chrome Extension
- ✅ **Text Detection**: Automatically shows "Capture" button when highlighting text
- ✅ **SQLite Database**: Full relational storage
- ✅ **AI Summarization**: Bullet-point summaries (mock or real LLM)
- ✅ **Smart Classification**: Auto-categorize by subject/topic
- ✅ **Keyword Extraction**: Automatically extract relevant keywords
- ✅ **Optional Notion Sync**: View notes in Notion (can be disabled)
- ✅ **RESTful API**: Query notes, topics, search data

### Backend
- ✅ **FastAPI Server**: `/capture` endpoint for processing
- ✅ **AI Summarization**: Bullet-point summaries (mock or real LLM)
- ✅ **Smart Classification**: Auto-categorize by subject/topic
- ✅ **Keyword Extraction**: Automatically extract relevant keywords
- ✅ **Notion Integration**: Save directly to database
- ✅ **Topic Management**: Create new or use existing topics

## � API Configuration

### Testing Without Setup (Mock Mode)
The extension works perfectly **without any API keys**:
- Backend returns mock summaries
- Perfect for demos and testing
- No Notion/OpenAI account needed

### Production Setup (Optional)

Create `backend/.env` from `.env.example`:

```env
NOTION_API_KEY=secret_xxxxx
NOTION_DATABASE_ID=xxxxx
OPENAI_API_KEY=sk-xxxxx
```

**Notion Database:**
1. Create integration at [Notion](https://www.notion.so/my-integrations)
2. Create database with properties:
   - Title (title)
   - Subject (select)
   - Topic (select)
   - Keywords (multi-select)
   - Source URL (url)
3. Share database with integration

**OpenAI (Optional):**
- Get API key from [OpenAI Platform](https://platform.openai.com/api-keys)

## � Why SQLite + Notion?

### SQLite Benefits
- **Full Control**: Your data, your rules
- **No Limits**: No API rate limits or quotas
- **Fast**: Local queries are instant
- **Offline**: Works without internet
- **Portable**: Single file backup
- **Queryable**: Build custom reports and analytics
- **Relational**: Proper foreign keys and joins

### Notion Benefits (Optional)
- **Visualization**: Beautiful interface for viewing
- **Organization**: Manual tagging and sorting
- **Collaboration**: Share with team/study group
- **Mobile**: Access from phone
- **Flexibility**: Customize views and filters

**Best of Both Worlds**: Store in SQLite, view in Notion!s

### `POST /capture`
Capture and process highlighted text.

**Request:**
```json
{
  "text": "Your highlighted text",
  "url": "https://source.com",
  "pageTitle": "Article Title"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "summary": ["Point 1", "Point 2"],
    "subject": "Computer Science",
    "topic": "Machine Learning",
    "keywords": ["AI", "neural networks"],
    "notion_url": "https://notion.so/..."
  }
}
```

### `GET /topics`
Get all existing topics from Notion.

### `GET /`
Health check endpoint.

## 🎨 Tech Stack

**Chrome Extension:**
- Manifest V3
- Vanilla JavaScript
- Tailwind CSS (CDN)
- Chrome Storage API
- Notifications API

**Backend:**
- FastAPI
- SQLite (primary database)
- Python 3.8+
- Notion API (optional sync)
- OpenAI API (optional LLM)

## 📖 Documentation

- Backend API docs: `http://localhost:8000/docs`
- Frontend README: `frontend/README.md`
- Backend README: `backend/README.md`

## 🎓 Use Cases

- **Students**: Capture lecture content and reading materials
- **Researchers**: Save excerpts from academic papers
- **Lifelong Learners**: Build knowledge base from articles
- **Professionals**: Organize work-related content

## 🔧 Development & Customization

### Modify Button Appearance
Edit `extension/styles/content.css`:
```css
.ai-study-capture-button {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  /* Change colors, size, position */
}
```

### Customize Popup UI
Edit `extension/popup.html` - uses Tailwind CSS classes

### Change Icons
Replace PNG files in `extension/icons/` (16x16, 48x48, 128x128)

### Test Changes
1. Make code changes
2. Go to `chrome://extensions/`
3. Click refresh icon on your extension
4. Test on any webpage

### Debug
- **Content Script**: Page console (F12)
- **Popup**: Right-click icon → Inspect
- **Background**: chrome://extensions/ → Service worker

## 🐛 Troubleshooting

**Button doesn't appear:**
- Ensure you highlighted >10 characters
- Refresh the page after installing extension
- Check browser console for errors (F12)

**Capture fails:**
- Verify backend is running: `http://localhost:8000`
- Check API URL in extension settings
- Look at Network tab in DevTools

**CORS errors:**
- Backend has CORS enabled by default
- Ensure backend is on port 8000

**Extension won't load:**
- Make sure all files are in `extension/` folder
- Check manifest.json syntax
- Look at chrome://extensions/ for error messages

## 📄 License

MIT License - Feel free to use for your hackathon!

---

Built with ❤️ for hackathons
