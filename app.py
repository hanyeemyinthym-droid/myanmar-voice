import os
import asyncio
import tempfile
import streamlit as st
import edge_tts

st.set_page_config(
    page_title="Myanmar Voice",
    page_icon=""
)

def get_secret(name):
    try:
        return st.secrets[name]
    except Exception:
        return os.getenv(name, "")

APP_USERNAME = get_secret("APP_USERNAME")
APP_PASSWORD = get_secret("APP_PASSWORD")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("Login")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login = st.form_submit_button("Login")

        if login:
            if username == APP_USERNAME and password == APP_PASSWORD:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Username or password is incorrect.")

    st.stop()

st.title(" Myanmar Voice")

text = st.text_area(
    "မြန်မာစာ",
    placeholder="အသံထုတ်ချင်တဲ့ မြန်မာစာကို ဒီမှာရေးပါ...",
    height=250,ū
    key="text"
)

voice = st.radio(
    "အသံရွေးပါ",
    ["Nilar", "Thiha"],
    horizontal=True
)

voice_id = {
    "Nilar": "my-MM-NilarNeural",
    "Thiha": "my-MM-ThihaNeural"
}[voice]

async def make_voice(text, voice_id):
    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".mp3"
    )
    temp_path = temp_file.name
    temp_file.close()

    communicate = edge_tts.Communicate(
        text=text,
        voice=voice_id
    )

    await communicate.save(temp_path)

    with open(temp_path, "rb") as f:
        audio_data = f.read()

    os.remove(temp_path)
    return audio_data

if st.button("Submit", type="primary"):
    if not text.strip():
        st.warning("မြန်မာစာ ထည့်ပေးပါ။")
    else:
        try:
            with st.spinner("အသံဖန်တီးနေပါတယ်..."):
                audio = asyncio.run(
                    make_voice(text, voice_id)
                )

            st.audio(audio, format="audio/mp3")

            st.download_button(
                "Download MP3",
                data=audio,
                file_name="myanmar_voice.mp3",
                mime="audio/mpeg"
            )

        except Exception as e:
            st.error(f"အသံဖန်တီးရာမှာ ပြဿနာဖြစ်ပါတယ်: {e}")

def clear_text():
    st.session_state.text = ""

st.button("Clear", on_click=clear_text)
