import os
import asyncio
import tempfile
import streamlit as st
import edge_tts

st.set_page_config(
    page_title="Myanmar Voice",
    page_icon="🔊"
)


def get_secret(name):
    try:
        return st.secrets[name]
    except Exception:
        return os.getenv(name, "")


APP_USERNAME = get_secret("APP_USERNAME")
APP_PASSWORD = get_secret("APP_PASSWORD")


# -------------------------
# Login
# -------------------------
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


# -------------------------
# Main App
# -------------------------
st.title("Myanmar Voice")

text = st.text_area(
    "မြန်မာစာ",
    placeholder="အသံထုတ်ချင်တဲ့ မြန်မာစာကို ဒီမှာရေးပါ...",
    height=350,
    key="text"
)

st.caption(f"စာလုံးအရေအတွက်: {len(text):,}")


voice = st.radio(
    "အသံရွေးပါ",
    ["Nilar", "Thiha"],
    horizontal=True
)

voice_id = {
    "Nilar": "my-MM-NilarNeural",
    "Thiha": "my-MM-ThihaNeural"
}[voice]


# -------------------------
# Speed
# -------------------------
speed = st.slider(
    "အသံမြန်နှုန်း",
    min_value=-50,
    max_value=50,
    value=0,
    step=5,
    help="0 = ပုံမှန်၊ အပေါင်း = မြန်၊ အနုတ် = နှေး"
)

if speed >= 0:
    rate = f"+{speed}%"
else:
    rate = f"{speed}%"


# -------------------------
# Pitch
# -------------------------
pitch_value = st.slider(
    "အသံအနိမ့် / အမြင့်",
    min_value=-50,
    max_value=50,
    value=0,
    step=5,
    help="0 = ပုံမှန်၊ အပေါင်း = အသံမြင့်၊ အနုတ် = အသံနိမ့်"
)

if pitch_value >= 0:
    pitch = f"+{pitch_value}Hz"
else:
    pitch = f"{pitch_value}Hz"


# -------------------------
# Split long text
# -------------------------
def split_long_text(text, max_chars=2500):
    text = text.strip()

    if len(text) <= max_chars:
        return [text]

    chunks = []
    current = ""

    # Burmese sentence ending mark ကိုသုံးပြီး ခွဲ
    parts = text.replace("။", "။\n").splitlines()

    for part in parts:
        part = part.strip()

        if not part:
            continue

        # စာကြောင်းတစ်ကြောင်းတည်း အရမ်းရှည်ရင် ဖြတ်
        while len(part) > max_chars:
            piece = part[:max_chars]
            part = part[max_chars:]

            if current:
                chunks.append(current.strip())
                current = ""

            chunks.append(piece.strip())

        if len(current) + len(part) + 1 <= max_chars:
            if current:
                current += " "
            current += part
        else:
            if current:
                chunks.append(current.strip())
            current = part

    if current:
        chunks.append(current.strip())

    return chunks


# -------------------------
# Create MP3
# -------------------------
async def make_voice(text, voice_id, rate, pitch):
    chunks = split_long_text(text)

    output_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".mp3"
    )
    output_path = output_file.name
    output_file.close()

    try:
        with open(output_path, "wb") as final_audio:
            for chunk in chunks:
                temp_file = tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".mp3"
                )
                temp_path = temp_file.name
                temp_file.close()

                try:
                    communicate = edge_tts.Communicate(
                        text=chunk,
                        voice=voice_id,
                        rate=rate,
                        pitch=pitch
                    )

                    await communicate.save(temp_path)

                    with open(temp_path, "rb") as f:
                        final_audio.write(f.read())

                finally:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)

        with open(output_path, "rb") as f:
            audio_data = f.read()

        return audio_data

    finally:
        if os.path.exists(output_path):
            os.remove(output_path)


# -------------------------
# Submit
# -------------------------
if st.button("အသံထုတ်မယ်", type="primary"):
    if not text.strip():
        st.warning("မြန်မာစာ အရင်ထည့်ပါ။")
    else:
        try:
            with st.spinner("အသံဖန်တီးနေပါတယ်..."):
                audio = asyncio.run(
                    make_voice(
                        text,
                        voice_id,
                        rate,
                        pitch
                    )
                )

            st.success("အသံဖန်တီးပြီးပါပြီ။")

            st.audio(
                audio,
                format="audio/mp3"
            )

            st.download_button(
                "Download MP3",
                data=audio,
                file_name="myanmar_voice.mp3",
                mime="audio/mpeg"
            )

        except Exception as e:
            st.error(f"အသံဖန်တီးရာမှာ ပြဿနာဖြစ်ပါတယ်: {e}")


# -------------------------
# Clear
# -------------------------
def clear_text():
    st.session_state.text = ""


st.button(
    "Clear",
    on_click=clear_text
            )
