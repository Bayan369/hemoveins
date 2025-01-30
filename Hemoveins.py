import streamlit as st
from huggingface_hub import InferenceClient

st.set_page_config(page_title="Hemoveins", page_icon="❤️")   
st.markdown("<h1 style='color:#941E11 ;'>Hemoveins</h1>",unsafe_allow_html=True)

API_KEY = open('secret').read()
client = InferenceClient(api_key=API_KEY)

with st.sidebar:
    st.markdown("""<style>emergency {border-radius: 8px;padding: 15px;margin: 15px 0;}</style>""", unsafe_allow_html=True)
    st.markdown('<div class="emergency">', unsafe_allow_html=True)
    st.markdown("## 🚨 Emergency Instructions🚨")
    st.markdown("""
    **Call 997 immediately if you have:**
    - Chest pain
    - Fever above 38.5°C
    - Difficulty breathing
    - Severe pain unrelieved by painkillers""")
    
    if st.button("Call Emergency Services🚑🆘", type="secondary", use_container_width=True):
        st.markdown('</div>', unsafe_allow_html=True)

sys_prompt = ("You are a doctor expert in sickle cell anemia. Your role has two phases:\n"
"1. Analyze patient answers and provide medical advice. For initial analysis consider:\n"
"- Water intake <3L → Hydration advice\n"
"- Temperature >37.8°C → Doctor visit\n"
"- Pain >7 → Emergency\n"
"- Medicine non-adherence → Importance of consistency\n"
"- Last crisis timing → Prevention tips\n"
"2. For follow-up questions: provide detailed, compassionate medical guidance." )


def hemobot(messages, stream=False):
    try:
        response = client.chat.completions.create(
            model="mistralai/Mistral-7B-Instruct-v0.3",
            messages=messages,
            max_tokens=250,
            stream=stream,
        )
        if stream:
            return (chunk.choices[0].delta.content for chunk in response)
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"
    

def update(role: str, content: str):
    """Updates the session_state messages with the given role and content."""
    st.session_state.messages.append({"role": role, "content": content})

if 'messages' not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": sys_prompt}]
    st.session_state.q_index = 0
    st.session_state.responses = {}
    st.session_state.analysis = False

questions = [
    ("water","How much water did you drink today? (in liters)"),
    ("temperature","What is your current temperature? (in Celsius)"),
    ("pain","How would you rate your pain (0-10)?"),
    ("medicine","Are you taking your medicine regularly?"),
    ("last_crisis","When was your last sickle cell crisis?")
]

if st.session_state.q_index == 0 and not st.session_state.analysis:
    st.markdown("Welcome to HemoBot - *Sickle Cell Anemia Advisor*. Let's assess your health through 5 quick questions.")


user_input = st.chat_input("How are you feeling today:")

if user_input:
    if st.session_state.q_index < len(questions):
        key, question = questions[st.session_state.q_index]
        st.session_state.responses[key] = user_input
        st.session_state.q_index += 1
    else:
        update(role="user", content=user_input)
        response = hemobot(st.session_state.messages, stream=True)
        #update(role="assistant", content=st.chat_message("HemoBot").write_stream(response))
        update(role="assistant", content=response)

if not st.session_state.analysis:
    if st.session_state.q_index < len(questions):
        current_key, current_question = questions[st.session_state.q_index]
        st.markdown(f"Question {st.session_state.q_index + 1}/{len(questions)}: {current_question}")
    else:
        result = "Patient's Responses:\n"
        for key, (_, question) in zip(st.session_state.responses.keys(), questions):
            result += f"- {question}: {st.session_state.responses[key]}\n"
        
        update(role="user", content=result)
        
        advice = hemobot(st.session_state.messages, stream=True)
        update(role="assistant", content=advice)
        
        st.session_state.analysis = True
        st.subheader("Medical Advice Based on Your Answers:")
        st.markdown("You can now ask any questions.")

st.markdown("""<style>[data-testid="stChatMessage"] {background-color: transparent !important;padding: 0 !important;box-shadow: none !important;}</style>""", unsafe_allow_html=True)
for msg in st.session_state.messages:
    if msg["role"] == "user" and "Patient's Responses" not in msg["content"]:
        with st.chat_message("user"):
            st.markdown(f'<div style="background-color: #FFF8E7; border-radius: 15px; padding: 15px; margin: 10px 0; max-width: 70%; margin-left: 30%;">'f'<span style="color: #565248; font-weight: bold;">You:</span><br>{msg["content"]}'f'</div>', unsafe_allow_html=True)
    elif msg["role"] == "assistant":
        with st.chat_message("assistant"):
            container = st.empty()
            if isinstance(msg['content'], str):
                container.markdown(f'<div style="background:#F9DCE0;border-radius:15px;padding:15px;margin:10px 0;max-width:70%;margin-right:30%">'f'<span style="color:#D7417D;font-weight:bold">HemoBot:</span>'f'<div style="margin-top:8px">{msg["content"]}</div>'f'</div>',unsafe_allow_html=True)
            else:
                full_response = ""
                for chunk in msg['content']:
                    full_response += chunk
                    container.markdown(f'<div style="background:#F9DCE0;border-radius:15px;padding:15px;margin:10px 0;max-width:70%;margin-right:30%">'f'<span style="color:#D7417D;font-weight:bold">HemoBot:</span>'f'<div style="margin-top:8px">{full_response}</div>'f'</div>',unsafe_allow_html=True)
                msg['content'] = full_response
