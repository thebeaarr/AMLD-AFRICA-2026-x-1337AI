#!/usr/bin/env python3
"""
Simple CLI tool to view and query the SQLite database
"""

import sqlite3
import sys
from datetime import datetime

DB_PATH = "study_assistant.db"


def print_table(headers, rows):
    """Print data in a formatted table"""
    if not rows:
        print("No data found.")
        return
    
    # Calculate column widths
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))
    
    # Print header
    header_row = " | ".join(h.ljust(w) for h, w in zip(headers, col_widths))
    print(header_row)
    print("-" * len(header_row))
    
    # Print rows
    for row in rows:
        print(" | ".join(str(cell).ljust(w) for cell, w in zip(row, col_widths)))


def show_topics():
    """Show all topics"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT t.id, t.name, t.subject, COUNT(n.id) as note_count
        FROM topics t
        LEFT JOIN notes n ON t.id = n.topic_id
        GROUP BY t.id
        ORDER BY t.name
    """)
    
    print("\n📚 TOPICS")
    print("=" * 70)
    print_table(["ID", "Topic", "Subject", "Notes"], cursor.fetchall())
    
    conn.close()


def show_notes(limit=10):
    """Show recent notes"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT n.id, n.title, t.name as topic, n.created_at
        FROM notes n
        JOIN topics t ON n.topic_id = t.id
        ORDER BY n.created_at DESC
        LIMIT ?
    """, (limit,))
    
    print(f"\n📝 RECENT NOTES (Last {limit})")
    print("=" * 70)
    print_table(["ID", "Title", "Topic", "Created"], cursor.fetchall())
    
    conn.close()


def show_note_details(note_id):
    """Show full details of a note"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get note info
    cursor.execute("""
        SELECT n.*, t.name as topic, t.subject
        FROM notes n
        JOIN topics t ON n.topic_id = t.id
        WHERE n.id = ?
    """, (note_id,))
    
    note = cursor.fetchone()
    if not note:
        print(f"❌ Note ID {note_id} not found")
        return
    
    # Get summary points
    cursor.execute("""
        SELECT point_text FROM summary_points
        WHERE note_id = ?
        ORDER BY point_order
    """, (note_id,))
    summary = cursor.fetchall()
    
    # Get keywords
    cursor.execute("""
        SELECT keyword FROM keywords
        WHERE note_id = ?
    """, (note_id,))
    keywords = cursor.fetchall()
    
    print(f"\n📄 NOTE DETAILS (ID: {note_id})")
    print("=" * 70)
    print(f"Title:      {note[1]}")
    print(f"Topic:      {note[-2]} ({note[-1]})")
    print(f"Created:    {note[6]}")
    if note[2]:
        print(f"Source:     {note[2]}")
    if note[7]:
        print(f"Notion:     {note[8]}")
    
    print(f"\nSummary:")
    for i, (point,) in enumerate(summary, 1):
        print(f"  {i}. {point}")
    
    print(f"\nKeywords:")
    print(f"  {', '.join(kw[0] for kw in keywords)}")
    
    print(f"\nOriginal Text:")
    print(f"  {note[5][:200]}..." if len(note[5]) > 200 else f"  {note[5]}")
    
    conn.close()


def show_stats():
    """Show database statistics"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM topics")
    topics_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM notes")
    notes_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM keywords")
    keywords_count = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT t.subject, COUNT(n.id) as count
        FROM topics t
        LEFT JOIN notes n ON t.id = n.topic_id
        GROUP BY t.subject
        ORDER BY count DESC
    """)
    by_subject = cursor.fetchall()
    
    print("\n📊 DATABASE STATISTICS")
    print("=" * 70)
    print(f"Total Topics:    {topics_count}")
    print(f"Total Notes:     {notes_count}")
    print(f"Total Keywords:  {keywords_count}")
    
    print(f"\nNotes by Subject:")
    for subject, count in by_subject:
        print(f"  {subject}: {count}")
    
    conn.close()


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python view_db.py stats          - Show statistics")
        print("  python view_db.py topics         - Show all topics")
        print("  python view_db.py notes [limit]  - Show recent notes")
        print("  python view_db.py note <id>      - Show note details")
        sys.exit(1)
    
    command = sys.argv[1]
    
    try:
        if command == "stats":
            show_stats()
        elif command == "topics":
            show_topics()
        elif command == "notes":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            show_notes(limit)
        elif command == "note":
            if len(sys.argv) < 3:
                print("❌ Please provide note ID")
                sys.exit(1)
            show_note_details(int(sys.argv[2]))
        else:
            print(f"❌ Unknown command: {command}")
            sys.exit(1)
    except sqlite3.OperationalError:
        print(f"❌ Database not found: {DB_PATH}")
        print("   Run the server first to create the database")
        sys.exit(1)


if __name__ == "__main__":
    main()
