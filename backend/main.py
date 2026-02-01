"""
FastAPI Backend for AI-Powered Student Study Assistant
A hackathon demo that captures highlighted text, summarizes it with AI,
stores it in SQLite database, and optionally syncs to Notion for viewing.

UPDATED: Now creates hierarchical categories in Notion:
Database → Subject → Topic → Individual Notes
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
import requests
import json
import sqlite3
from datetime import datetime
from contextlib import contextmanager
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

# Load environment variables
load_dotenv()

app = FastAPI(title="Study Assistant API")

# CORS middleware to allow Chrome extension and all origins (for hackathon demo)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (Chrome extension + any webpage)
    allow_credentials=False,  # Must be False when allow_origins is "*"
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2")  # Default to llama2, can use mistral, codellama, etc.
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")  # Default Ollama URL
DB_PATH = os.getenv("DB_PATH", "study_assistant.db")
SYNC_TO_NOTION = os.getenv("SYNC_TO_NOTION", "true").lower() == "true"

print(f"notion api key: {NOTION_API_KEY}")
print(f"notion database id: {NOTION_DATABASE_ID}")
print(f"ollama model: {OLLAMA_MODEL}")

# Request/Response Models
class CaptureRequest(BaseModel):
    text: str
    url: Optional[str] = ""
    pageTitle: Optional[str] = ""

class LLMResponse(BaseModel):
    subject: str
    topic: str
    create_new: bool
    keywords: str  # comma-separated


# ========== DATABASE FUNCTIONS ==========

@contextmanager
def get_db():
    """Context manager for database connections"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def get_all_topics() -> List[dict]:
    """Fetch all topics from database"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, subject FROM topics ORDER BY name")
        return [{"id": row[0], "name": row[1], "subject": row[2]} for row in cursor.fetchall()]


def get_or_create_topic(topic_name: str, subject: str) -> int:
    """Get topic ID or create if doesn't exist"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Try to find existing topic
        cursor.execute("SELECT id FROM topics WHERE name = ?", (topic_name,))
        result = cursor.fetchone()
        
        if result:
            return result[0]
        
        # Create new topic
        cursor.execute(
            "INSERT INTO topics (name, subject) VALUES (?, ?)",
            (topic_name, subject)
        )
        conn.commit()
        print(f"➕ Created new topic: {topic_name} ({subject})")
        return cursor.lastrowid


def save_note_to_db(
    title: str,
    topic_id: int,
    keywords: str,
    source_url: str,
    original_text: str
) -> int:
    """Save note to database"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Insert into summaries table (summary_text = original_text since we're not summarizing)
        cursor.execute("""
            INSERT INTO summaries (title, topic_id, original_text, summary_text, keywords, source_url)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (title, topic_id, original_text, original_text, keywords, source_url))
        
        conn.commit()
        note_id = cursor.lastrowid
        print(f"💾 Saved note to database (ID: {note_id})")
        return note_id


def get_note_details(note_id: int) -> Optional[dict]:
    """Get full note details"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Get note with topic info
        cursor.execute("""
            SELECT s.*, t.name as topic_name, t.subject
            FROM summaries s
            JOIN topics t ON s.topic_id = t.id
            WHERE s.id = ?
        """, (note_id,))
        
        note_row = cursor.fetchone()
        if not note_row:
            return None
        
        return {
            "id": note_row["id"],
            "title": note_row["title"],
            "topic": note_row["topic_name"],
            "subject": note_row["subject"],
            "original_text": note_row["original_text"],
            "summary_text": note_row["summary_text"],
            "keywords": note_row["keywords"],
            "source_url": note_row["source_url"],
            "created_at": note_row["created_at"]
        }


# ========== NOTION SYNC FUNCTIONS (UPDATED FOR HIERARCHICAL ORGANIZATION) ==========

def find_or_create_category_page(parent_id: str, title: str, is_database: bool = True) -> str:
    """
    Find or create a category page (Subject or Topic).
    Returns the page ID.
    
    This creates the hierarchical structure:
    - Subject pages are created in the database
    - Topic pages are created inside Subject pages
    """
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }
    
    # Search for existing page with this title
    search_url = "https://api.notion.com/v1/search"
    search_payload = {
        "query": title,
        "filter": {"property": "object", "value": "page"}
    }
    
    try:
        response = requests.post(search_url, json=search_payload, headers=headers)
        response.raise_for_status()
        results = response.json().get("results", [])
        
        # Check if we found a matching page
        for result in results:
            page_title = ""
            if "properties" in result:
                # It's a database page
                title_prop = result["properties"].get("Name", result["properties"].get("title", {}))
                if title_prop.get("title"):
                    page_title = title_prop["title"][0]["plain_text"]
            elif "title" in result:
                # It's a regular page
                if result["title"]:
                    page_title = result["title"][0]["plain_text"]
            
            if page_title == title:
                print(f"📁 Found existing category: {title}")
                return result["id"]
        
        # Create new category page if not found
        print(f"📁 Creating new category: {title}")
        create_url = "https://api.notion.com/v1/pages"
        
        parent_payload = {"page_id": parent_id}
        
        # For regular pages (not database pages), use lowercase "title"
        create_payload = {
            "parent": parent_payload,
            "properties": {
                "title": {  # Changed from "Name" to "title" for regular pages
                    "title": [{"text": {"content": title}}]
                }
            }
        }
        
        response = requests.post(create_url, json=create_payload, headers=headers)
        response.raise_for_status()
        page = response.json()
        return page["id"]
        
    except Exception as e:
        print(f"Error finding/creating category: {e}")
        raise


def insert_note_to_notion(
    title: str,
    summary: List[str],
    subject: str,
    topic: str,
    keywords: List[str],
    source_url: str
) -> dict:
    """
    Insert a new note with hierarchical organization:
    Database → Subject → Topic → Note
    
    Example structure:
    📚 Study Notes Database
       └─ 📖 Computer Science (Subject page)
          └─ 💡 Machine Learning (Topic page)
             └─ 📝 Your note here (Note page)
    """
    if not NOTION_API_KEY or not NOTION_DATABASE_ID:
        print("⚠️ Notion credentials not set, returning mock response")
        return {"id": "mock-page-id", "url": "https://notion.so/mock-page"}
    
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }
    
    try:
        # Step 1: Find or create Subject page (e.g., "Computer Science")
        print(f"📚 Finding/creating Subject: {subject}")
        subject_page_id = find_or_create_category_page(
            parent_id=NOTION_DATABASE_ID,
            title=subject,
            is_database=True
        )
        
        # Step 2: Find or create Topic page under Subject (e.g., "Machine Learning")
        print(f"💡 Finding/creating Topic: {topic} under {subject}")
        topic_page_id = find_or_create_category_page(
            parent_id=subject_page_id,
            title=topic,
            is_database=False
        )
        
        # Step 3: Create the actual note as a sub-page under Topic
        print(f"📝 Creating note: {title}")
        
        # Format summary as bullet points - filter out empty strings
        summary_blocks = [
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": point}}]
                }
            }
            for point in summary if point.strip()
        ]
        
        # Add source URL and keywords as additional blocks
        additional_blocks = []
        
        if source_url and source_url.strip():
            additional_blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {"type": "text", "text": {"content": "🔗 Source: "}},
                        {"type": "text", "text": {"content": source_url, "link": {"url": source_url}}}
                    ]
                }
            })
        
        if keywords:
            keywords_text = ", ".join([kw for kw in keywords if kw.strip()])
            if keywords_text:
                additional_blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {"type": "text", "text": {"content": "🏷️ Keywords: "}},
                            {"type": "text", "text": {"content": keywords_text}}
                        ]
                    }
                })
        
        # Create the note page
        url = "https://api.notion.com/v1/pages"
        payload = {
            "parent": {"page_id": topic_page_id},
            "properties": {
                "title": [{"text": {"content": title[:2000]}}]
            },
            "children": summary_blocks + additional_blocks
        }
        
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        page = response.json()
        
        print(f"✅ Created note hierarchy: {subject} → {topic} → {title}")
        
        return {
            "id": page["id"],
            "url": page["url"]
        }
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ Notion API Error: {e}")
        print(f"Response: {e.response.text}")
        raise HTTPException(status_code=500, detail=f"Failed to save to Notion: {e.response.text}")
    except Exception as e:
        print(f"Error inserting to Notion: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save to Notion: {str(e)}")


def sync_note_to_notion(note_id: int) -> dict:
    """
    Sync a note to Notion for viewing/organization.
    This is optional - data is already saved in SQLite.
    """
    if not NOTION_API_KEY or not NOTION_DATABASE_ID:
        print("⚠️ Notion sync disabled or credentials not set")
        return {"id": "notion-disabled", "url": ""}
    
    # Get note data from database
    note_data = get_note_details(note_id)
    if not note_data:
        return {"id": "note-not-found", "url": ""}
    
    try:
        # Split original text into paragraphs for Notion blocks (or use as single item)
        original_text = note_data["original_text"]
        # Split by newlines and filter empty lines, or use as single block
        text_paragraphs = [p.strip() for p in original_text.split('\n') if p.strip()]
        if not text_paragraphs:
            text_paragraphs = [original_text]
        
        # Convert comma-separated keywords string to list
        keywords_list = [kw.strip() for kw in note_data["keywords"].split(',')] if note_data["keywords"] else []
        
        # Sync to Notion
        page = insert_note_to_notion(
            title=note_data["title"],
            summary=text_paragraphs,  # Using original text in summary blocks
            subject=note_data["subject"],
            topic=note_data["topic"],
            keywords=keywords_list,
            source_url=note_data["source_url"]
        )
        
        print(f"✅ Synced to Notion: {page['url']}")
        return {
            "id": page["id"],
            "url": page["url"]
        }
    except Exception as e:
        print(f"⚠️ Error syncing to Notion (data still saved locally): {e}")
        # Don't raise - data is already saved in SQLite
        return {"id": "notion-error", "url": ""}


# ========== LLM FUNCTIONS ==========

def call_llm_for_classification(text: str, existing_topics: List[str]) -> LLMResponse:
    """
    Call Ollama LLM via LangChain to classify the highlighted text.
    
    Uses local open-source models like llama2, mistral, or codellama.
    Returns subject, topic, and keywords (no summarization - text stored as-is).
    """
    
    try:
        # Initialize Ollama LLM with LangChain
        print(f"🤖 Using Ollama model: {OLLAMA_MODEL}")
        llm = OllamaLLM(
            model=OLLAMA_MODEL,
            base_url=OLLAMA_BASE_URL,
            temperature=0.7
        )
        
        # Create prompt template
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", "You are an expert study assistant that classifies academic content. You MUST respond with ONLY valid JSON - no other text, explanations, or markdown."),
            ("user", """Your task is to analyze the given text and determine its academic classification.

STEP 1 - Identify the Subject:
Read the text carefully and determine which academic field it belongs to. Common subjects include:
- Environmental Science (sustainability, climate, water, pollution, ecosystems)
- Engineering (civil, mechanical, electrical, chemical, environmental)
- Computer Science (programming, algorithms, AI, data structures, software)
- Mathematics (algebra, calculus, statistics, geometry)
- Physics (mechanics, thermodynamics, electromagnetism, quantum)
- Chemistry (organic, inorganic, biochemistry, reactions)
- Biology (anatomy, genetics, ecology, microbiology)
- Social Sciences (psychology, sociology, economics, political science)
- Business (management, marketing, finance, entrepreneurship)
- Medicine (anatomy, pharmacology, diseases, treatments)
- Agriculture (farming, crops, soil science, livestock)
- Architecture (building design, urban planning, structures)
- If the text doesn't clearly fit any category, use "General Studies"

STEP 2 - Identify the Specific Topic:
Within the subject, determine the specific topic or subtopic. Examples:
- Environmental Science → Water Conservation, Climate Change, Renewable Energy
- Computer Science → Web Development, Machine Learning, Databases
- Biology → Cell Biology, Genetics, Ecosystems

STEP 3 - Check Existing Topics:
Existing topics in the system: {existing_topics}

If a very similar topic exists (similar meaning, not exact match), set "create_new": false and use the existing topic name.
If this is a genuinely new topic, set "create_new": true and provide a clear topic name.

STEP 4 - Extract Keywords:
List 3-5 key terms that represent the main concepts in the text (comma-separated).

Text to analyze:
{text}

Respond with ONLY this JSON structure (no markdown, no code blocks, no explanations):
{{
  "subject": "the academic subject",
  "topic": "the specific topic",
  "create_new": false,
  "keywords": "keyword1, keyword2, keyword3"
}}""")
        ])
        
        # Format and invoke
        chain = prompt_template | llm
        response = chain.invoke({
            "existing_topics": ', '.join(existing_topics) if existing_topics else "None",
            "text": text[:1000]  # Limit text length for faster processing
        })
        
        print(f"📝 LLM Response: {response[:200]}...")
        
        # Try to extract JSON from response
        # Some models might add extra text, so we look for JSON block
        llm_output = response.strip()
        
        # If response contains markdown code blocks, extract JSON
        if "```json" in llm_output:
            llm_output = llm_output.split("```json")[1].split("```")[0].strip()
        elif "```" in llm_output:
            llm_output = llm_output.split("```")[1].split("```")[0].strip()
        
        # Find JSON object in the response
        start_idx = llm_output.find('{')
        end_idx = llm_output.rfind('}') + 1
        if start_idx != -1 and end_idx > start_idx:
            llm_output = llm_output[start_idx:end_idx]
        
        # Parse JSON response
        parsed = json.loads(llm_output)
        return LLMResponse(**parsed)
        
    except Exception as e:
        print(f"⚠️ LLM Error: {e}")
        print("📋 Falling back to simple analysis...")
        
        # Fallback: Simple keyword-based classification
        text_lower = text.lower()
        
        # Detect subject based on keywords (expanded list)
        subject = "General Studies"
        topic = "Study Notes"
        
        # Environmental Science & Sustainability
        if any(word in text_lower for word in ['water', 'harvesting', 'rainwater', 'conservation', 'sustainability', 'climate', 'environment', 'ecosystem', 'pollution', 'renewable', 'solar', 'wind']):
            subject = "Environmental Science"
            if any(word in text_lower for word in ['water', 'harvesting', 'rainwater']):
                topic = "Water Conservation"
            elif any(word in text_lower for word in ['climate', 'warming', 'carbon']):
                topic = "Climate Change"
            elif any(word in text_lower for word in ['solar', 'wind', 'renewable']):
                topic = "Renewable Energy"
            else:
                topic = "Sustainability"
        
        # Engineering
        elif any(word in text_lower for word in ['engineering', 'design', 'structure', 'construction', 'circuit', 'mechanical', 'electrical']):
            subject = "Engineering"
            topic = "General Engineering"
        
        # Computer Science
        elif any(word in text_lower for word in ['algorithm', 'code', 'programming', 'software', 'computer', 'database', 'javascript', 'python', 'api']):
            subject = "Computer Science"
            if any(word in text_lower for word in ['web', 'html', 'css', 'frontend', 'backend']):
                topic = "Web Development"
            elif any(word in text_lower for word in ['machine learning', 'ai', 'neural', 'model']):
                topic = "Machine Learning"
            else:
                topic = "Programming"
        
        # Mathematics
        elif any(word in text_lower for word in ['math', 'equation', 'theorem', 'calculate', 'algebra', 'calculus', 'geometry']):
            subject = "Mathematics"
            topic = "General Math"
        
        # Physics
        elif any(word in text_lower for word in ['physics', 'force', 'energy', 'quantum', 'velocity', 'momentum']):
            subject = "Physics"
            topic = "General Physics"
        
        # Chemistry
        elif any(word in text_lower for word in ['chemistry', 'molecule', 'reaction', 'atom', 'compound', 'element']):
            subject = "Chemistry"
            topic = "General Chemistry"
        
        # Biology
        elif any(word in text_lower for word in ['biology', 'cell', 'dna', 'organism', 'genetics', 'protein']):
            subject = "Biology"
            topic = "General Biology"
        
        # Agriculture
        elif any(word in text_lower for word in ['agriculture', 'farming', 'crop', 'soil', 'harvest', 'livestock', 'irrigation']):
            subject = "Agriculture"
            topic = "Farming & Crops"
        
        # Business
        elif any(word in text_lower for word in ['business', 'marketing', 'management', 'finance', 'entrepreneur', 'startup']):
            subject = "Business"
            topic = "General Business"
        
        # Medicine/Health
        elif any(word in text_lower for word in ['medicine', 'health', 'disease', 'treatment', 'patient', 'medical', 'anatomy']):
            subject = "Medicine"
            topic = "General Medicine"
        
        # Extract simple keywords (first few meaningful words)
        words = text.split()
        keywords = [w.strip('.,!?') for w in words[:10] if len(w) > 4][:5]
        keywords_str = ', '.join(keywords) if keywords else "study, notes"
        
        return LLMResponse(
            subject=subject,
            topic=existing_topics[0] if existing_topics else topic,
            create_new=False,
            keywords=keywords_str
        )



# ========== API ENDPOINTS ==========

@app.get("/")
def root():
    """API health check and info"""
    with get_db() as db:
        topics_count = db.execute("SELECT COUNT(*) as count FROM topics").fetchone()["count"]
        notes_count = db.execute("SELECT COUNT(*) as count FROM summaries").fetchone()["count"]
    
    return {
        "status": "running",
        "message": "AI Study Assistant API",
        "version": "2.0.0",
        "database": DB_PATH,
        "topics_count": topics_count,
        "notes_count": notes_count,
        "notion_sync": SYNC_TO_NOTION
    }


@app.get("/topics")
def get_topics_endpoint():
    """Get all existing topics from database"""
    topics = get_all_topics()
    return {"topics": topics}


@app.get("/notes")
def get_notes(limit: int = 50, offset: int = 0):
    """Get all notes from database"""
    with get_db() as db:
        cursor = db.execute("""
            SELECT s.id, s.title, s.created_at, t.name as topic, t.subject
            FROM summaries s
            JOIN topics t ON s.topic_id = t.id
            ORDER BY s.created_at DESC
            LIMIT ? OFFSET ?
        """, (limit, offset))
        
        notes = []
        for row in cursor.fetchall():
            notes.append({
                "id": row["id"],
                "title": row["title"],
                "topic": row["topic"],
                "subject": row["subject"],
                "created_at": row["created_at"]
            })
        
        return {"notes": notes, "limit": limit, "offset": offset}


@app.get("/notes/{note_id}")
def get_note(note_id: int):
    """Get full details of a specific note"""
    note = get_note_details(note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@app.post("/capture")
def capture_text(request: CaptureRequest):
    """
    Main endpoint: Capture highlighted text and save to database.
    
    Process:
    1. Fetch existing topics from database
    2. Call LLM to classify the text (determine subject and topic)
    3. Save original text to SQLite database (no summarization)
    4. Optionally sync to Notion with hierarchical organization
    """
    
    try:
        # Step 1: Fetch existing topics from database
        print("📚 Fetching existing topics from database...")
        existing_topics = get_all_topics()
        topic_names = [t["name"] for t in existing_topics]
        print(f"Found {len(existing_topics)} existing topics")
        
        # Step 2: Call LLM for classification
        print("🤖 Calling LLM for text analysis...")
        llm_result = call_llm_for_classification(request.text, topic_names)
        print(f"LLM Result: {llm_result}")
        
        # Step 3: Get or create topic in database
        topic_id = get_or_create_topic(llm_result.topic, llm_result.subject)
        
        # Step 4: Save to SQLite database (original text stored as-is)
        print("💾 Saving to SQLite database...")
        title = request.pageTitle or f"{llm_result.subject} - {llm_result.topic}"
        
        note_id = save_note_to_db(
            title=title,
            topic_id=topic_id,
            keywords=llm_result.keywords,
            source_url=request.url or "",
            original_text=request.text
        )
        
        # Step 5: Optionally sync to Notion
        notion_url = ""
        if SYNC_TO_NOTION:
            print("📤 Syncing to Notion...")
            notion_result = sync_note_to_notion(note_id)
            notion_url = notion_result.get("url", "")
        
        print(f"✅ Successfully saved note #{note_id}")
        
        # Return success response
        return {
            "success": True,
            "message": "Note saved successfully!",
            "data": {
                "note_id": note_id,
                "subject": llm_result.subject,
                "topic": llm_result.topic,
                "keywords": llm_result.keywords,
                "notion_url": notion_url,
                "saved_to_db": True,
                "synced_to_notion": SYNC_TO_NOTION and notion_url != ""
            }
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)