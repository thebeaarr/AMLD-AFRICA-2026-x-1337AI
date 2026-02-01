# AI Study Assistant - Backend

FastAPI backend for the AI-powered student study assistant.

## Architecture

- **Primary Storage**: SQLite database for all data (topics, notes, summaries, keywords)
- **Optional Sync**: Notion for viewing and organization (can be disabled)
- **AI Processing**: OpenAI API for summarization (falls back to mock mode)

This design gives you full control over your data while still allowing Notion integration for visualization.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env:
   # - DB_PATH: SQLite database file path (default: study_assistant.db)
   # - SYNC_TO_NOTION: true/false to enable/disable Notion sync
   # - Add Notion/OpenAI keys if desired (optional)
   ```

3. **Set up Notion (Optional):**
   
   Only needed if you want to sync notes to Notion for viewing:
   
   Create a Notion database with these properties:
   - `Title` (title)
   - `Subject` (select)
   - `Topic` (select)
   - `Keywords` (multi-select)
   - `Source URL` (url)
   
   Share the database with your integration and copy the database ID.
   
   Set `SYNC_TO_NOTION=true` in `.env`

4. **Run the server:**
   ```bash
   python main.py
   ```
   
   The database will be automatically initialized on first run.
   
   Or with uvicorn directly:
   ```bash
   uvicorn main:app --reload
   ```

TheDatabase Schema

### Topics Table
- `id`: Primary key
- `name`: Topic name (unique)
- `subject`: Subject category
- `created_at`: Timestamp

### Notes Table
- `id`: Primary key
- `title`: Note title
- `topic_id`: Foreign key to topics
- `source_url`: Original webpage URL
- `page_title`: Webpage title
- `original_text`: Highlighted text
- `notion_page_id`: Notion page ID (if synced)
- `notion_url`: Notion page URL (if synced)
- `created_at`: Timestamp

### Summary Points Table
- `id`: Primary key
- `note_id`: Foreign key to notes
- `ponote_id": 1,
    "summary": ["bullet 1", "bullet 2"],
    "subject": "Computer Science",
    "topic": "Machine Learning",
    "keywords": ["AI", "neural networks"],
    "notion_url": "https://notion.so/...",
    "saved_to_db": true,
    "synced_to_notion": true
  }
}
```

### `GET /topics`
Get all topics from SQLite database.

### `GET /notes`
Get all notes with pagination.

**Query params:**
- `limit`: Number of notes (default: 50)
- `offset`: Pagination offset (default: 0)

### `GET /notes/{note_id}`
Get full details of a specific note including summary and keywords
### `POST /capture`
Capture highlighted text and save to Notion.

**Request:**
```json
{
  "text": "Your highlighted text here",
  "url": "https://example.com/article",
  "pageTitle": "Optional page title"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Note saved successfully!",
  "data": {
    "summary": ["bullet 1", "bullet 2"],
    "subject": "Computer Science",
    "topic": "Machine Learning",
    "keywords": ["AI", "neural networks"],
**Returns:**
- Server status
- Database path
- Topics count
- Notion sync status

## Configuration Options

### Database
- `DB_PATH`: SQLite database file location (default: `study_assistant.db`)

### Notion Sync
- `SYNC_TO_NOTION`: Enable/disable Notion sync (`true`/`false`)
- `NOTION_API_KEY`: Your Notion integration token
- `NOTION_DATABASE_ID`: Target Notion database ID

### LLM
- `OPENAI_API_KEY`: OpenAI API key for real classification (optional)

## Testing Without API Keys

The backend works perfectly without any external API keys:
- SQLite database stores everything locally
- LLM returns mock summaries
- Notion sync is disabled
- Perfect for development and testing!

## Benefits of SQLite + Notion Architecture

### SQLite Advantages
✅ Full control over your data
✅ Fast queries and filtering
✅ No API rate limits
✅ Works offline
✅ Easy to backup and migrate
✅ Relational data integrity
✅ Can build complex queries

### Notion Integration
✅ Beautiful visualization
✅ Manual organization and tagging
✅ Collaborative features
✅ Mobile apps
✅ Optional - can be disabled

## Data Export

Your SQLite database (`study_assistant.db`) contains all your data and can be:
- Backed up by simply copying the file
- Queried with any SQLite client
- Exported to CSV, JSON, etc.
- Migrated to other database
### `GET /topics`
Get all existing topics from Notion.

### `GET /`
Health check endpoint.

## Testing Without API Keys

The backend works in "mock mode" without API keys:
- LLM calls return placeholder summaries
- Notion operations are logged but not executed
- Perfect for testing the flow without setting up integrations

## API Documentation

Interactive API docs available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
