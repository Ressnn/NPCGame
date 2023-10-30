import streamlit as st

st.set_page_config(
    page_title="Start",
    page_icon="👋", #Change
)

if st.secrets["API_KEY"] != None:
    print("Secrets Loaded") #If statement will create an error if the API_KEY is not set!

st.write("## The Prince Has Gone Missing!")
st.write("\t This is an interactive adventure where you will enter the 1600s with an important mission. You are a guest of the newly constructed Charlottenburg Palace in order to attend the young prince Friedrich Wilhelm of Hanover’s seventh birthday banquet. Unfortunately, the young prince has gone missing, with no one in the palace able to locate him. You are well known to have good intuition and to be a figure of authority, so you are tasked with retrieving the young prince unharmed before the banquet. In order to locate the young prince, you will explore the gardens and interact with people at various locations throughout the grounds. WARNING: The NPC's only have a basic understanding of locations and will often point you in the incorrect direction or tell you to use a misleading mode of transportation. Use your map to see possible locations of other NPCs and google maps to find landmarks.")
st.write("\t To start, locate NPCs using your map on the sidebar. Interact with them to collect clues on the prince's location.")
st.sidebar.success("Procced by Searching for NPC's on the map.")
