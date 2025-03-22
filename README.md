# Social Media Post Generator

An AI-powered tool that generates platform-specific social media posts with integrated web research capabilities.

## Features

- **Intelligent Research**: Uses AI to gather and analyze information from the web
- **Platform-Specific Formatting**: Optimizes content for different social media platforms
- **Tone Control**: Adjust content tone (informative, casual, professional, etc.)
- **Web Search Integration**: Automatically researches topics using web search and scraping
- **Content Validation**: Ensures posts meet platform-specific requirements
- **Enhanced Formatting**: 
  - Platform-specific structure and layout
  - Strategic use of emojis and formatting
  - Proper spacing and organization
  - Professional call-to-actions
  - Optimized hashtag placement

## Supported Platforms

- **LinkedIn**: Professional networking with rich formatting
  - Bold, italic, and list support
  - Up to 5 hashtags
  - Professional tone and structure
  - Media and link support

- **Instagram**: Visual-first content
  - Up to 30 hashtags
  - Strategic emoji usage
  - Line breaks for readability
  - No clickable links in captions

- **Facebook**: Social engagement
  - Up to 10 hashtags
  - Rich formatting support
  - Interactive elements
  - Media and link support

- **X (Twitter)**: Concise messaging
  - 280 character limit
  - Up to 5 hashtags
  - Strategic emoji usage
  - No line breaks

## Prerequisites

- Python 3.8 or higher
- Chrome browser (for web scraping)
- OpenAI API key

## Installation

1. Clone the repository:
```powershell
git clone https://github.com/yourusername/social-media-post-generator.git
cd social-media-post-generator
```

2. Create and activate a virtual environment:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

3. Install dependencies:
```powershell
pip install -r requirements.txt
```

4. Set up environment variables:
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

Here's an example of a well-formatted LinkedIn post:

```
🌟 The Impact of Artificial Intelligence on Healthcare in 2024 🌟

As we progress into 2024, the role of artificial intelligence (AI) in the healthcare industry is becoming increasingly transformative, particularly in the realms of diagnostics and patient care.

Key Insights:
• The global healthcare AI market is projected to surge from $11.2 billion in 2023 to $427.5 billion by 2032
• AI-related publications in healthcare have jumped from 158 in 2014 to 731 in 2024
• AI is empowering patients through personalized care solutions
• Ethical discussions around data privacy and algorithmic fairness are growing

The conversation around AI in healthcare is more than just technological advancement; it's about transforming patient experiences and outcomes.

What are your thoughts on the ethical implications of AI in healthcare? Let's engage!

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
│   ├── config.py          # Configuration settings
│   ├── prompts.py         # System prompts and formatting rules
│   └── cli.py             # Command line interface
├── requirements.txt
├── setup.ps1
├── .env
└── README.md
```

## Configuration

### Platform Settings
Platform-specific settings can be modified in `src/config.py`:
- Character limits
- Hashtag limits
- Formatting rules
- Platform-specific constraints

### Research Settings
Research parameters can be adjusted in `src/researcher_agent.py`:
- Number of search results
- Focus areas
- Output structure

### Formatting Rules
Formatting rules and prompts can be customized in `src/prompts.py`:
- Platform-specific formatting guidelines
- Structure requirements
- Tone and style preferences

## Development

### Running Tests
```powershell
python -m pytest tests/
```

### Adding New Platforms
1. Add platform configuration in `config.py`
2. Add platform-specific prompts in `prompts.py`
3. Update platform validation in `agent.py`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for GPT models
- LangChain for the agent framework
- DuckDuckGo for web search capabilities 