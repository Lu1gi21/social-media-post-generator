"""Command-line interface for the social media post generator.

This module provides a command-line interface for generating social media posts
from topic files. It supports multiple platforms and allows customization of
post tone and formatting. The generated posts are saved in an organized
directory structure for easy access and management.

Usage:
    python -m src.cli topic.txt --title "My Post" --platforms instagram linkedin

TODO:
- Add support for interactive mode
- Implement post preview functionality
- Add support for post scheduling
- Implement post analytics
- Add support for batch processing
- Implement post templates
- Add support for custom output formats
"""

import argparse
import os
from pathlib import Path
from typing import List, Dict

from .agent import SocialMediaAgent

def read_topic_file(file_path: str) -> str:
    """Read the topic from a text file.
    
    This function reads the content of a text file that contains the topic
    for social media post generation. The file should be UTF-8 encoded.
    
    Args:
        file_path: Path to the topic file
        
    Returns:
        str: Content of the topic file, with leading/trailing whitespace removed
        
    Raises:
        FileNotFoundError: If the specified file doesn't exist
        UnicodeDecodeError: If the file is not UTF-8 encoded
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read().strip()

def save_post(content: str, title: str, platform: str) -> None:
    """Save the generated post to a file.
    
    This function saves the generated social media post to a file in an organized
    directory structure. For X/Twitter threads, each tweet is saved as a separate
    file. The output is stored in an 'output' directory, with subdirectories for
    each topic.
    
    Args:
        content: The post content to save
        title: The title of the post (used for directory and file naming)
        platform: The social media platform the post is for
        
    Note:
        - Creates an 'output' directory if it doesn't exist
        - Creates a topic-specific subdirectory
        - Handles X/Twitter threads differently from other platforms
        - Sanitizes filenames for cross-platform compatibility
    """
    # Create output directory if it doesn't exist
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Create a safe filename from the title (remove special characters)
    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
    safe_title = safe_title.replace(' ', '-')
    
    # Create topic-specific directory
    topic_dir = output_dir / safe_title
    topic_dir.mkdir(exist_ok=True)
    
    # Handle platform-specific saving logic
    if platform == "x":
        # For X/Twitter, save each tweet in the thread as a separate file
        tweets = content.split("\n\n---\n\n")
        for i, tweet in enumerate(tweets, 1):
            filename = f"x_tweet_{i}.txt"
            filepath = topic_dir / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(tweet.strip())
            print(f"Generated tweet {i} saved to: {filepath}")
    else:
        # For other platforms, save as a single file
        filename = f"{platform}.txt"
        filepath = topic_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Generated post saved to: {filepath}")

def main():
    """Main CLI entry point.
    
    TODO:
    - Add support for interactive mode
    - Implement post preview functionality
    - Add support for post scheduling
    - Implement post analytics
    - Add support for batch processing
    - Implement post templates
    - Add support for custom output formats
    
    This function implements the command-line interface for the social media
    post generator. It parses command-line arguments, reads the topic file,
    and generates posts for specified platforms using the SocialMediaAgent.
    
    Command-line Arguments:
        topic_file: Path to the file containing the topic
        --title: Title for the generated posts (required)
        --platforms: List of platforms to generate posts for (default: all)
        --tone: Tone for the generated posts (default: "neutral")
        
    Example:
        python -m src.cli topic.txt --title "My Post" --platforms instagram linkedin
    """
    # Set up command-line argument parser
    parser = argparse.ArgumentParser(description="Generate social media posts from a topic file")
    parser.add_argument("topic_file", help="Path to the file containing the topic")
    parser.add_argument("--title", help="Title for the generated posts", required=True)
    parser.add_argument("--platforms", nargs="+", default=["instagram", "linkedin", "facebook", "x"],
                      help="Platforms to generate posts for")
    parser.add_argument("--tone", default="neutral",
                      help="Tone for the generated posts")
    
    # Parse command-line arguments
    args = parser.parse_args()
    
    # Read the topic file
    try:
        topic = read_topic_file(args.topic_file)
    except FileNotFoundError:
        print(f"Error: Topic file '{args.topic_file}' not found")
        return
    
    # Initialize the social media agent
    agent = SocialMediaAgent()
    
    # Generate posts for each specified platform
    for platform in args.platforms:
        try:
            # Generate post for current platform
            post = agent.generate_post(
                content=topic,
                platform=platform,
                tone=args.tone
            )
            # Save the generated post
            save_post(post, args.title, platform)
        except ValueError as e:
            print(f"Error generating post for {platform}: {e}")
        except Exception as e:
            print(f"Unexpected error generating post for {platform}: {e}")

if __name__ == "__main__":
    main() 