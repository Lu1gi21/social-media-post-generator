# Social Media Post Generator

An AI-powered tool that generates platform-specific social media posts with integrated web research capabilities and Gen Z optimization.

## About

Social Media Post Generator is a powerful tool designed to help content creators, marketers, and social media managers create engaging, platform-optimized content. It leverages advanced AI technology to research topics, generate content, and format posts according to each platform's best practices.

### Key Features

- **Intelligent Research**: Uses AI to gather and analyze information from the web
- **Platform-Specific Formatting**: Optimizes content for different social media platforms
- **Gen Z Optimization**: 
  - Authentic Gen Z language and style
  - Modern emoji usage and combinations
  - Relatable content and experiences
  - Current internet culture references
- **Tone Control**: Adjust content tone (informative, casual, professional, etc.)
- **Web Search Integration**: Automatically researches topics using web search and scraping
- **Content Validation**: Ensures posts meet platform-specific requirements
- **Research Caching**: Efficient caching of research results to improve performance
- **Enhanced Formatting**: 
  - Platform-specific structure and layout
  - Strategic use of emojis and formatting
  - Proper spacing and organization
  - Professional call-to-actions
  - Optimized hashtag placement

## System Flow

1. **Research Phase**:
   - Takes input topic
   - Performs web research using DuckDuckGo and web scraping
   - Analyzes information for social media angles
   - Caches research results for future use
   - Prepares structured research data

2. **Content Generation Phase**:
   - Uses platform-specific prompts
   - Generates initial content with basic formatting
   - Applies Gen Z style and language
   - Optimizes emoji usage based on platform

3. **Formatting Phase**:
   - Applies platform-specific formatting rules
   - Adds appropriate hashtags
   - Ensures proper spacing and structure
   - Validates content length and constraints

4. **Validation Phase**:
   - Checks platform-specific requirements
   - Validates character limits
   - Ensures hashtag limits are respected
   - Finalizes the post

## Supported Platforms

- **LinkedIn**: Professional networking with rich formatting
  - Bold, italic, and list support
  - Up to 5 hashtags
  - Professional tone with Gen Z authenticity
  - Media and link support
  - Strategic emoji usage

- **Instagram**: Visual-first content
  - Up to 30 hashtags
  - Gen Z-optimized emoji usage
  - Line breaks for readability
  - No clickable links in captions
  - Modern internet culture references

- **Facebook**: Social engagement
  - Up to 10 hashtags
  - Rich formatting support
  - Interactive elements
  - Media and link support
  - Relatable Gen Z content

- **X (Twitter)**: Concise messaging
  - 280 character limit
  - Up to 5 hashtags
  - Strategic emoji usage
  - No line breaks
  - Viral tweet formats

## Gen Z Features

### Emoji Guide
The system includes a comprehensive Gen Z emoji guide with:
- Modern emoji usage (🫡, 🫣, 🫢, 🫥, 🫤)
- Common combinations (💀😭, 💅✨)
- Platform-specific emoji styles
- Natural and authentic usage patterns

### Language Style
- Current Gen Z slang and expressions
- Relatable experiences and perspectives
- Modern internet culture references
- Authentic voice and tone
- Platform-appropriate style

### Content Structure
- Attention-grabbing openings
- Clear, concise messaging
- Strategic formatting
- Engaging call-to-actions
- Optimized hashtag placement

## Prerequisites

- Python 3.8 or higher
- Chrome browser (for web scraping)
- OpenAI API key
- PowerShell 7.0 or higher (for Windows users)

## Installation

1. Clone the repository:
```powershell
git clone https://github.com/yourusername/social-media-post-generator.git
cd social-media-post-generator
```

2. Run the setup script:
```powershell
.\setup.ps1
```

This will:
- Create and activate a virtual environment
- Install all required dependencies
- Set up the environment variables
- Configure the development environment

3. Set up environment variables:
Create a `.env` file in the root directory with your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

## Usage

### Basic Usage

```python
from src.agent import SocialMediaAgent

# Initialize the agent
agent = SocialMediaAgent()

# Generate a post
post = agent.generate_post(
    content="Latest developments in AI technology",
    platform="linkedin",
    tone="professional"
)

print(post)
```

### Command Line Interface

```powershell
# Generate a single platform post
python -m src.cli example_topic.txt --title "AI in Healthcare 2024" --platforms linkedin

# Generate posts for multiple platforms
python -m src.cli example_topic.txt --title "AI in Healthcare 2024" --platforms instagram linkedin facebook x --tone professional
```

### Example Output

Here's an example of a Gen Z-optimized LinkedIn post:

```
🚀 The Future of AI in Healthcare: A Gen Z Perspective 🧠

Y'all won't believe how AI is revolutionizing healthcare! Let me break it down for you 💅

Key Stats That'll Blow Your Mind:
• Healthcare AI market: $11.2B → $427.5B by 2032 🫡
• AI publications: 158 (2014) → 731 (2024) 📈
• Patient empowerment through AI: absolutely game-changing 🎯

The tea is: it's not just about fancy tech - it's about making healthcare accessible and personalized for everyone. And that's the real flex 💪

What are your thoughts on AI in healthcare? Drop them below! 👇

#HealthTech #AIinHealthcare #PatientEmpowerment #HealthcareInnovation #AIethics
```

### Advanced Usage

```python
from src.researcher_agent import ResearcherAgent

# Use the researcher agent directly for detailed research
researcher = ResearcherAgent()
research_results = researcher.research_topic(
    topic="AI technology",
    focus_areas=["current developments", "key statistics", "social media angles"]
)

# Access structured research results
print(research_results["summary"])
print(research_results["key_facts"])
print(research_results["trends"])
print(research_results["sources"])
```

## Project Structure

```
social-media-post-generator/
├── src/
│   ├── __init__.py
│   ├── agent.py           # Main agent implementation
│   ├── researcher_agent.py # Research capabilities
│   ├── web_search.py      # Web search and scraping
│   ├── research_cache.py  # Research result caching
│   ├── config.py          # Configuration settings
│   ├── prompts.py         # System prompts and formatting rules
│   └── cli.py             # Command line interface
├── output/                # Generated posts output directory
├── requirements.txt
├── setup.ps1             # PowerShell setup script
├── .env
└── README.md
```

## Configuration

### Platform Settings
Platform-specific settings can be modified in `src/config.py`:
- Character limits
- Hashtag limits
- Emoji support
- Formatting rules
- Platform-specific constraints

### Research Settings
Research parameters can be adjusted in `src/researcher_agent.py`:
- Number of search results
- Focus areas
- Output structure
- Cache settings

### Formatting Rules
Formatting rules and prompts can be customized in `src/prompts.py`:
- Platform-specific formatting guidelines
- Structure requirements
- Tone and style preferences
- Gen Z emoji guide

## Development

### Running Tests
```powershell
python -m pytest tests/
```

### Dependencies
The project uses the following key dependencies:
- langgraph==0.0.15
- openai>=1.12.0
- langchain>=0.1.9
- beautifulsoup4>=4.12.0
- selenium>=4.18.1
- duckduckgo-search>=4.1.1
- trafilatura>=1.6.3

For a complete list of dependencies, see `requirements.txt`.

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## Security

For security concerns, please see our [Security Policy](SECURITY.md).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- OpenAI for providing the GPT models
- The open-source community for various tools and libraries
- Contributors and maintainers of this project 