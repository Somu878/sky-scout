# FlightFinder Pro 🛫

A powerful flight search application that combines Streamlit, LangChain, and Browserbase to provide intelligent flight search capabilities.

## Features

- 🔍 Real-time flight search using Kayak
- 🤖 AI-powered search and summarization using DeepSeek-R1 model
- 🌐 Web scraping capabilities with Browserbase
- 📊 Clean and intuitive Streamlit interface
- 💡 Transparent thinking process display

## Prerequisites

- Python 3.9 or higher
- Ollama installed and running locally
- Browserbase API key
- DeepSeek-R1 model available in Ollama

## Installation

1. Clone the repository:
```bash
git clone <>
cd flight-finder_pro
```

2. Create and activate a virtual environment:
```bash
python -m venv flightfinder_env
source flightfinder_env/bin/activate  # On Windows: flightfinder_env\Scripts\activate
```

3. Install required packages:
```bash
pip install streamlit langchain-community playwright beautifulsoup4
```

4. Install Playwright browsers:
```bash
playwright install
```

5. Set up environment variables:
```bash
export BROWSERBASE_API_KEY="your_browserbase_api_key"
```

## Running the Application

1. Make sure Ollama is running with DeepSeek-R1 model:
```bash
ollama run deepseek-r1
```

2. Start the Streamlit application:
```bash
streamlit run app.py
```

## Project Structure

- `app.py`: Main Streamlit application interface
- `flight_finder.py`: Core logic for flight search and AI processing
- Components:
  - Flight Search Agent: Handles flight search using Kayak and Browserbase
  - Summarization Agent: Processes and summarizes flight results
  - Custom UI Components: Separate thinking process and results display

## How It Works

1. User inputs flight search criteria (departure city, destination city, and date)
2. The application generates a Kayak search URL
3. Browserbase scrapes flight data from Kayak
4. LangChain agents process and summarize the results
5. Results are displayed with a separated thinking process and flight information

## Environment Variables

Required environment variables:
- `BROWSERBASE_API_KEY`: Your Browserbase API key for web scraping

## Dependencies

- `streamlit`: Web application framework
- `langchain-community`: AI/LLM toolkit
- `playwright`: Browser automation
- `beautifulsoup4`: HTML parsing
- `ollama`: Local LLM model hosting

## Error Handling

The application includes comprehensive error handling for:
- Invalid search queries
- Missing API keys
- Web scraping failures
- LLM processing errors

## Contributing

Feel free to submit issues and enhancement requests!

## License

[Your chosen license] 