import openai
import os
import streamlit as st
from streamlit_chat import message
from vincenty import vincenty
from streamlit_js_eval import get_geolocation
from PIL import Image

openai.api_key = os.getenv('API_KEY')

npc = {
"name" : "Gottfried Wilhelm Leibniz",
"input" : "The man doesn’t know that the prince is missing. When you ask him about the prince, he becomes disturbed and asks for more details. He becomes worried about Sophie Charlotte and says he must find her, and he does not give you more information until you question him again. When you ask him where you might find the prince, he pauses to think. Then a flash of insight comes to him, as he realizes the prince loved the little island because of his pretend fiefdom there. He tells you that the boy was bringing supplies, such as boats,  on the island, so you should check there. Then he hurries off with his notebook and quill to find his patron Sophie Charlotte.",
"near" : "Mausoleum",
"description" : "The mausoleum looms at the back of the clearing. Before the main clearing, you see a man with a mop of black hair bent over a notebook on a bench. He taps his quill against his cheek and does not look up as you approach, until you block the sun across his notebook with your shadow. You see inscrutable mathematical equations in the notebook before he snaps it shut and looks up to you with a perturbed air of someone interrupted while on the verge of a major discovery.",
"icon" : "📙",
"lat" : 52.524,
"lng" : 13.29183,
"img" : "Philosopher"
}


base_prompt  = """Pretend you are an NPC in an AR application, with the following as a section of your character. You will use this information to interact with a USER, one to three sentences at a time, in response to what the USER asks. You will gradually tell the story, adding details as needed and guide the USER to the next area. Your character’s context will follow.

CHARACTER DETAILS:
"""

# Setting page title and header
st.set_page_config(page_title=npc["name"], page_icon=npc["icon"])

def vincenty_dist(lat, lng, lat1,lng1):
    return vincenty((lat,lng),(lat1,lng1), miles=False)

loc = get_geolocation()
if loc != None:
    print(loc)
    if vincenty_dist(loc["coords"]["latitude"], loc["coords"]["longitude"], npc["lat"], npc["lng"]) >= .05:
        st.write("## Not close enough to this NPC!")
        exit()

st.markdown("<h1 style='text-align: center;'>" + npc["name"] + " - " + npc["near"] +  "</h1>", unsafe_allow_html=True)
st.markdown(npc["description"])

with st.columns(3)[1]:
    try:
        if npc["img"] != None:
            image = Image.open('./pages/static/' + npc["img"] + ".png")
            st.image(image, caption='Image of ' + npc["name"])
    except:
        pass

# Initialise session state variables
if npc["name"] + 'generated' not in st.session_state:
    st.session_state[npc["name"] + 'generated'] = []
if npc["name"] + 'past' not in st.session_state:
    st.session_state[npc["name"] + 'past'] = []
if npc["name"] + 'messages' not in st.session_state:
    st.session_state[npc["name"] + 'messages'] = [
        {"role": "system", "content": base_prompt + npc["input"]}
    ]
if npc["name"] + 'model_name' not in st.session_state:
    st.session_state[npc["name"] + 'model_name'] = []
if npc["name"] + 'cost' not in st.session_state:
    st.session_state[npc["name"] + 'cost'] = []
if npc["name"] + 'total_tokens' not in st.session_state:
    st.session_state[npc["name"] + 'total_tokens'] = []
if npc["name"] + 'total_cost' not in st.session_state:
    st.session_state[npc["name"] + 'total_cost'] = 0.0
# Sidebar - let user choose model, show total cost of current conversation, and let user clear the current conversation
st.sidebar.title("Sidebar")
model_name = "GPT-3.5"
model = "gpt-3.5-turbo"
counter_placeholder = st.sidebar.empty()
#counter_placeholder.write(f"Total cost of this conversation: ${st.session_state['total_cost']:.5f}")
clear_button = st.sidebar.button("Clear Conversation", key="clear")

# reset everything
if clear_button:
    st.session_state[npc["name"] + 'generated'] = []
    st.session_state[npc["name"] + 'past'] = []
    st.session_state[npc["name"] + 'messages'] = [
        {"role": "system", "content": base_prompt + npc["input"]}
    ]
    st.session_state[npc["name"] + 'number_tokens'] = []
    st.session_state[npc["name"] + 'model_name'] = []
    st.session_state[npc["name"] + 'cost'] = []
    st.session_state[npc["name"] + 'total_cost'] = 0.0
    st.session_state[npc["name"] + 'total_tokens'] = []

# generate a response
def generate_response(prompt):
    st.session_state[npc["name"] + 'messages'].append({"role": "user", "content": prompt})

    completion = openai.ChatCompletion.create(
        model=model,
        messages=st.session_state[npc["name"] + 'messages']
    )
    response = completion.choices[0].message.content
    st.session_state[npc["name"] + 'messages'].append({"role": "assistant", "content": response})

    # print(st.session_state['messages'])
    total_tokens = completion.usage.total_tokens
    prompt_tokens = completion.usage.prompt_tokens
    completion_tokens = completion.usage.completion_tokens
    return response, total_tokens, prompt_tokens, completion_tokens


# container for chat history
response_container = st.container()
# container for text box
container = st.container()

with container:
    with st.form(key='my_form', clear_on_submit=True):
        user_input = st.text_area("You:", key='input', height=100)
        submit_button = st.form_submit_button(label='Send')

    if submit_button and user_input:
        output, total_tokens, prompt_tokens, completion_tokens = generate_response(user_input)
        st.session_state[npc["name"] + 'past'].append(user_input)
        st.session_state[npc["name"] + 'generated'].append(output)
        st.session_state[npc["name"] + 'model_name'].append(model_name)
        st.session_state[npc["name"] + 'total_tokens'].append(total_tokens)

        # from https://openai.com/pricing#language-models
        if model_name == "GPT-3.5":
            cost = total_tokens * 0.002 / 1000
        else:
            cost = (prompt_tokens * 0.03 + completion_tokens * 0.06) / 1000

        st.session_state[npc["name"] + 'cost'].append(cost)
        st.session_state[npc["name"] + 'total_cost'] += cost

if st.session_state[npc["name"] + 'generated']:
    with response_container:
        for i in range(len(st.session_state[npc["name"] + 'generated'])):
            message(st.session_state[npc["name"] + "past"][i], is_user=True, key=str(i) + '_user' , avatar_style="shapes")
            message(st.session_state[npc["name"] + "generated"][i], key=str(i), avatar_style="shapes", seed=npc["name"])
