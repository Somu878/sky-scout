import streamlit as st
from flight_finder import find_flights

def display_thinking_process(message):
    """Custom component to display thinking process"""
    with st.expander("🤔 Thinking Process", expanded=True):
        st.markdown(f"""
        <div style='background-color: #f0f2f6; padding: 15px; border-radius: 5px;'>
            {message}
        </div>
        """, unsafe_allow_html=True)

def display_flight_results(results):
    """Custom component to display flight results"""
    with st.container():
        st.markdown("### ✈️ Flight Results")
        st.markdown(f"""
        <div style='background-color: #e6f3ff; padding: 15px; border-radius: 5px;'>
            {results}
        </div>
        """, unsafe_allow_html=True)

# Streamlit UI
st.title("✈️ FlightFinder Pro")
st.subheader("Powered by Browserbase and LangChain")

# Input form
departure_city = st.text_input("Departure City", "SF")
destination_city = st.text_input("Destination City", "New York")
travel_date = st.text_input("Travel Date", "21st September")
search_button = st.button("Search Flights")

# Handle search
if search_button:
    if not departure_city or not destination_city or not travel_date:
        st.error("Please fill in all fields.")
    else:
        query = f"{departure_city} to {destination_city} on {travel_date}"
        with st.spinner("Searching for flights..."):
            result = find_flights(query)
            
            if "Error" in result:
                st.error(result)
            else:
                # Split the result into thinking process and actual results
                if "<think>" in result:
                    think_parts = result.split("<think>")
                    if len(think_parts) > 1:
                        thinking = think_parts[0]
                        results = think_parts[1]
                        display_thinking_process(thinking)
                        display_flight_results(results)
                else:
                    # If no thinking process is present, just display results
                    display_flight_results(result)