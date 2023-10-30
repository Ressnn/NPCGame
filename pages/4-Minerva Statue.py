import openai
import os
import streamlit as st
from streamlit_chat import message
from vincenty import vincenty
from streamlit_js_eval import get_geolocation
from PIL import Image

openai.api_key = os.getenv('API_KEY')

npc = {
"name" : "Statue of Minerva",
"input" : "A statue of Minerva, which does not have a conversation but instead gives a message once it is asked for advice. The message is as follows: \"You are seeking guidance on your mission for the lost prince. To find his most loved one, approach the main garden. She will be near the flowers, with overwhelming hope in her heart that he will be returned safely.\" After giving that message, any further queries are met with the following message: \"The statue’s steely eyes urge you to continue north to the flowerbeds.\"",
"near" : "Statue",
"description" : "You are combing the green expanse of the gardens when you suddenly come across yet another statue. You can tell that she is Minerva through her strong posture and air of calculated violence.  Her sharp gaze is highlighted by a ray of sunlight breaking from the tree. You feel an urge to stop and reflect on the statue, because although there are innumerable fixtures in the gardens this one has an aura. Somehow, words will come from the stone, and you feel an urge to address her for advice.",
"icon" : "🗿",
"lat" : 52.52161,
"lng" : 13.29343,
"img" : None}


base_prompt  = """Pretend you are an NPC in an AR application, with the following as a section of your character. You will use this information to interact with a USER, one to three sentences at a time, in response to what the USER asks in short, conversational lines. You will gradually tell the story, adding details as needed and guide the USER to the next area. Your character’s context will follow.

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
