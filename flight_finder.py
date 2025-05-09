import os
from datetime import datetime
from langchain_community.llms import Ollama
from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

# Initialize the DeepSeek-R1 model via Ollama
llm = Ollama(model="deepseek-r1", base_url="http://localhost:11434")

# --- Tools ---

def kayak_tool(query: str) -> str:
    """Generate a Kayak search URL from a user query."""
    try:
        parts = query.lower().split(" to ")
        if len(parts) != 2:
            return "Invalid query format. Use: 'SF to New York on 21st September'"

        departure_city = parts[0].strip()
        rest = parts[1].split(" on ")
        if len(rest) != 2:
            return "Invalid query format. Specify date like 'on 21st September'"

        destination_city = rest[0].strip()
        date_str = rest[1].strip()

        # Parse the date
        travel_date = datetime.strptime(date_str, "%dth %B").replace(year=datetime.now().year)
        date_formatted = travel_date.strftime("%Y-%m-%d")

        # Map city names to airport codes (simplified)
        city_to_code = {"sf": "SFO", "new york": "NYC", "los angeles": "LAX", "chicago": "ORD"}
        departure_code = city_to_code.get(departure_city, "SFO")
        destination_code = city_to_code.get(destination_city, "NYC")

        # Construct Kayak URL
        kayak_url = f"https://www.kayak.com/flights/{departure_code}-{destination_code}/{date_formatted}?sort=bestflight_a"
        return kayak_url
    except Exception as e:
        return f"Error generating Kayak URL: {str(e)}"

kayak_tool = Tool(
    name="Kayak Tool",
    func=kayak_tool,
    description="Generate a Kayak search URL from a user query like 'SF to New York on 21st September'."
)

def browserbase_tool(url: str) -> str:
    """Scrape flight data from a given URL using a headless browser."""
    api_key = os.getenv("BROWSERBASE_API_KEY")
    if not api_key:
        return "Browserbase API key not found."

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.connect_over_cdp(
                f"wss://connect.browserbase.com?apiKey={api_key}"
            )
            context = browser.contexts[0]
            page = context.pages[0]
            page.goto(url)
            
            # Wait for flight results to load (adjust selector based on Kayak's HTML)
            page.wait_for_selector(".resultWrapper", timeout=30000)
            html = page.content()
            browser.close()

            # Parse with BeautifulSoup
            soup = BeautifulSoup(html, "html.parser")
            flights = soup.select(".resultWrapper")[:5]  # Top 5 flights
            flight_data = []
            for flight in flights:
                # Extract flight details (adjust selectors based on Kayak's HTML structure)
                airline = flight.select_one(".airlineName").text if flight.select_one(".airlineName") else "Unknown"
                times = flight.select_one(".departureTime").text + " - " + flight.select_one(".arrivalTime").text if flight.select_one(".departureTime") and flight.select_one(".arrivalTime") else "N/A"
                duration = flight.select_one(".duration").text if flight.select_one(".duration") else "N/A"
                price = flight.select_one(".price").text if flight.select_one(".price") else "N/A"
                flight_data.append(f"{airline}: {times}, Duration: {duration}, Price: {price}")
            return "\n".join(flight_data) if flight_data else "No flights found."
    except Exception as e:
        return f"Error scraping flights: {str(e)}"

browserbase_tool = Tool(
    name="Browserbase Tool",
    func=browserbase_tool,
    description="Scrape flight data from a given URL using a headless browser."
)

# --- Agents ---

# Custom prompt to ensure the LLM includes Action Input
agent_prompt = """
You are a flight search assistant. Your task is to find flights based on the user's query. You have access to the following tools:
- Kayak Tool: Generates a Kayak search URL from a user query.
- Browserbase Tool: Scrapes flight data from a given URL.

For each step, you must follow this exact format:

Thought: [Your reasoning about what to do]
Action: [The action to take, e.g., "Kayak Tool"]
Action Input: [The input to the action, e.g., "SF to New York on 21st September"]
Observation: [The result of the action, filled in by the system]

If you need to use a tool, you MUST include both the Action and Action Input lines. Do not skip the Action Input line. If you have the final answer, use:

Final Answer: [Your final answer]

Now, proceed with the user's query: {query}
"""

# Flight Search Agent with improved prompt and error handling
flight_search_agent = initialize_agent(
    tools=[kayak_tool, browserbase_tool],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True,  # Automatically retry on parsing errors
    agent_kwargs={"system_prompt": agent_prompt}  # Custom prompt
)

def search_flights(query: str) -> str:
    """Run the flight search agent with a user query."""
    prompt = f"Find flights for the following query: {query}. Use the Kayak Tool to generate a URL, then use the Browserbase Tool to scrape the flight data."
    try:
        result = flight_search_agent.run(prompt)
        return result
    except Exception as e:
        return f"Error in flight search: {str(e)}"

# Summarization Agent
summarization_prompt = PromptTemplate(
    input_variables=["flight_data"],
    template="Summarize the following flight data into a concise list of the top 5 flights, including airlines, departure/arrival times, duration, and price:\n{flight_data}"
)

summarization_chain = LLMChain(llm=llm, prompt=summarization_prompt)

def summarize_flights(flight_data: str) -> str:
    """Run the summarization chain on the flight data."""
    try:
        return summarization_chain.run(flight_data=flight_data)
    except Exception as e:
        return f"Error in summarization: {str(e)}"

# --- Workflow ---

def find_flights(query: str) -> str:
    """Run the flight finder workflow with a user query."""
    # Step 1: Search for flights
    flight_data = search_flights(query)
    if "Error" in flight_data:
        return flight_data
    
    # Step 2: Summarize the results
    summary = summarize_flights(flight_data)
    return summary