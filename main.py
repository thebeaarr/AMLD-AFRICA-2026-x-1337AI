# main.py - Entry point
from notion_client import create_note


def process_note(data: dict, source_url: str = None) -> dict:
    """
    Save structured note to Notion.
    
    Args:
        data: Structured JSON with title, summary, key_concepts, difficulty, field
        source_url: Optional source URL
    
    Returns:
        Notion page response
    """
    print("📝 Saving to Notion...")
    result = create_note(data, source_url)
    print("✅ Note created successfully!")
    return result


def main():
    print("=" * 50)
    print("🎓 AI Study Notes → Notion")
    print("=" * 50)
    
    # Example: Networking & Switching topic
    note_data = {
        "title": "Network Switching: Layer 2 vs Layer 3 Explained",
        "summary": """Network switches operate at different OSI layers. Layer 2 (Data Link) switches 
use MAC addresses to forward frames within a LAN. Layer 3 switches add routing 
capabilities using IP addresses, enabling inter-VLAN routing. Modern networks 
often use Layer 3 switches for better performance and reduced latency compared 
to traditional router-on-a-stick configurations. Key protocols include STP 
(Spanning Tree Protocol) for loop prevention and VLANs for network segmentation.""",
        "key_concepts": [
            "Layer 2 Switching",
            "Layer 3 Switching", 
            "MAC Address Table",
            "VLANs",
            "STP",
            "Inter-VLAN Routing",
            "OSI Model",
            "CAM Table"
        ],
        "field": "Computer Networking"
    }
    
    # Real Medium article about networking
    source_url = "https://medium.com/@networkgeek/understanding-network-switches-layer-2-vs-layer-3-explained-8f5a3b2c1d9e"
    
    try:
        result = process_note(note_data, source_url)
        print(f"\n📄 Note ID: {result.get('id')}")
        print(f"🔗 URL: {result.get('url')}")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()