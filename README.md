# AMLD-AFRICA-2026-x-1337AI



# AI-Powered Structured Study Notes → Notion

## 📌 Overview

This project is an **AI-assisted note-taking system** designed for students. It automatically transforms articles or learning resources into **clean, structured study notes** and stores them in a **Notion database**.

Instead of taking manual notes, students provide a source (article URL or text), and the system:

1. Extracts the content
2. Uses AI to structure the knowledge
3. Saves the result into Notion as organized, searchable notes

Notion acts as the **knowledge base**, while the AI acts as the **thinking and structuring engine**.

---

## 🎯 Problem Statement

Students often:

* Read long articles without retaining key ideas
* Take unstructured or inconsistent notes
* Lose track of sources

This project solves that by:

* Enforcing **structured note-taking**
* Automatically linking notes to their original sources
* Centralizing everything inside Notion

---

## 🧠 Core Idea

> **AI understands the content. Notion stores the knowledge.**

The AI does *not* manage data persistence or organization. Its only role is to:

* Understand learning content
* Extract meaningful structure
* Output clean, machine-readable data

Notion is used strictly as a storage and organization layer.

---

## 🏗️ System Architecture

```
Student Input (URL / Text)
        ↓
Content Extraction (Python)
        ↓
AI Processing (LLM)
        ↓
Structured JSON Output
        ↓
Notion API
        ↓
Notion Database (Study Notes)
```

Each step has a **single responsibility**, keeping the system simple and reliable.

---

## 📊 Notion Database Design

Each note is stored as **one page (row)** inside a Notion database.

### Database Properties

| Property Name | Type         | Description                   |
| ------------- | ------------ | ----------------------------- |
| Title         | Title        | Main topic of the note        |
| Summary       | Text         | Concise explanation           |
| Key Concepts  | Multi-select | Extracted keywords            |
| Source URL    | URL          | Original article              |
| Difficulty    | Select       | Easy / Medium / Hard          |
| Field         | Select       | Subject area (CS, Math, etc.) |
| Created By AI | Checkbox     | Always true                   |
| Date Added    | Date         | Auto-generated                |

This schema is fixed and intentionally minimal.

---

## 🤖 AI Output Format (Critical)

The AI **must return valid JSON only**.

Example:

```json
{
  "title": "TCP vs UDP",
  "summary": "TCP is connection-oriented and reliable, while UDP is connectionless and faster.",
  "key_concepts": ["TCP", "UDP", "Networking"],
  "difficulty": "Medium",
  "field": "Computer Science"
}
```

This JSON is mapped **directly** to Notion properties.

---

## 🗂️ Project Structure

```
ai-notion-notes/
│
├── main.py               # Entry point
├── config.py             # API keys and IDs
├── content_loader.py     # Extract content from URL or text
├── ai_processor.py       # AI prompting and JSON parsing
├── notion_client.py      # All Notion API logic
└── requirements.txt
```

---

## 🔁 Execution Flow

1. Student submits an article URL or raw text
2. Content is extracted into plain text
3. AI processes the text and returns structured JSON
4. Python maps the JSON to Notion properties
5. A new page (note) is created inside the Notion database

---

## 🔐 Security Considerations

* Notion API tokens are stored **server-side only**
* Tokens are never exposed to the frontend
* The Notion integration has access only to shared pages

---

## 🚀 Hackathon Value

This project demonstrates:

* Real-world AI usage
* Clean system design
* Practical automation
* A usable end product

It can easily be extended with:

* PDF support
* Note linking (relations)
* Flashcards or summaries

---

## 🧩 Key Principle

> **AI thinks. Notion stores. Students learn.**

This separation of concerns keeps the system scalable, understandable, and effect
