"""Command-line interface for the social media post generator."""

import argparse
import os
from pathlib import Path
from typing import List, Dict

from .agent import SocialMediaAgent

def read_topic_file(file_path: str) -> str:
    """Read the topic from a text file.
    
    Args:
        file_path: Path to the topic file
        
    Returns:
        Content of the topic file
        
    Raises:
        FileNotFoundError: If the file doesn't exist
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read().strip()

def save_post(content: str, title: str, platform: str) -> None:
    """Save the generated post to a file.
    
    Args:
        content: The post content
        title: The title of the post
        platform: The social media platform
    """
    # Create output directory if it doesn't exist
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Create a safe filename from the title
    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
    safe_title = safe_title.replace(' ', '-')
    
    # Save the post
    filename = f"{safe_title}-{platform}.txt"
    filepath = output_dir / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Generated post saved to: {filepath}")

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Generate social media posts from a topic file")
    parser.add_argument("topic_file", help="Path to the file containing the topic")
    parser.add_argument("--title", help="Title for the generated posts", required=True)
    parser.add_argument("--platforms", nargs="+", default=["instagram", "linkedin", "facebook", "x"],
                      help="Platforms to generate posts for")
    parser.add_argument("--tone", default="neutral",
                      help="Tone for the generated posts")
    
    args = parser.parse_args()
    
    # Read the topic
    try:
        topic = read_topic_file(args.topic_file)
    except FileNotFoundError:
        print(f"Error: Topic file '{args.topic_file}' not found")
        return
    
    # Initialize the agent
    agent = SocialMediaAgent()
    
    # Generate posts for each platform
    for platform in args.platforms:
        try:
            post = agent.generate_post(
                content=topic,
                platform=platform,
                tone=args.tone
            )
            save_post(post, args.title, platform)
        except ValueError as e:
            print(f"Error generating post for {platform}: {e}")
        except Exception as e:
            print(f"Unexpected error generating post for {platform}: {e}")

if __name__ == "__main__":
    main() 