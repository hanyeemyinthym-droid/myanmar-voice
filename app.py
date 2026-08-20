import os
import tempfile
import gradio as gr
import edge_tts

async def make_voice(text, voice):
    if not text.strip():
        raise gr.Error("မြန်မာစာ ထည့်ပေးပါ")

    if voice == "Nilar":
        voice_id = "my-MM-NilarNeural"
    else:
        voice_id = "my-MM-ThihaNeural"

    output = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".mp3"
    ).name

    await edge_tts.Communicate(
        text,
        voice_id
    ).save(output)

    return output


with gr.Blocks(title="Myanmar Voice") as app:
    gr.Markdown("# Myanmar Voice")

    text = gr.Textbox(
        label="မြန်မာစာ",
        placeholder="အသံထုတ်ချင်တဲ့ မြန်မာစာကို ဒီမှာထည့်ပါ...",
        lines=10
    )

    voice = gr.Radio(
        ["Nilar", "Thiha"],
        value="Nilar",
        label="အသံရွေးပါ"
    )

    clear = gr.ClearButton([text])
    submit = gr.Button("Submit")

    audio = gr.Audio(
        type="filepath",
        label="အသံ"
    )

    submit.click(
        make_voice,
        inputs=[text, voice],
        outputs=audio
    )


username = os.environ["APP_USERNAME"]
password = os.environ["APP_PASSWORD"]

app.launch(
    server_name="0.0.0.0",
    server_port=int(os.environ.get("PORT", 7860)),
    auth=(username, password)
)
