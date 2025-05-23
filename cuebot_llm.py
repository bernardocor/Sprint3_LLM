
import gradio as gr
from PyPDF2 import PdfReader
import requests

# URL de la API desplegada de FastAPI
API_URL = "http://localhost:8000/cuebot/"

CORPUS_TEXT = ""

def add_file(history, file):
    """
    Procesa el archivo PDF subido y almacena el texto en CORPUS_TEXT.
    """
    with open(file.name, 'rb') as pdf_file:
        pdf_reader = PdfReader(pdf_file)
        extracted_text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                extracted_text += page_text
    global CORPUS_TEXT
    CORPUS_TEXT = extracted_text
    history.append({"role": "assistant", "content": "Archivo PDF cargado correctamente."})
    return history

def add_text(history, text):
    """
    Agrega el texto del usuario al historial del chat.
    """
    history.append({"role": "user", "content": text})
    return history, gr.update(value="", interactive=False)

def bot(history):
    """
    Envía el texto del usuario y el corpus cargado al endpoint FastAPI y muestra la respuesta.
    """
    if not CORPUS_TEXT:
        respuesta = "Primero debes cargar un archivo PDF."
    else:
        # Encuentra el último mensaje del usuario
        for msg in reversed(history):
            if msg["role"] == "user":
                instruccion = msg["content"]
                break
        data = {"instruccion": instruccion, "texto": CORPUS_TEXT}
        try:
            r = requests.post(API_URL, json=data)
            respuesta = r.json().get("respuesta", "No se pudo procesar la respuesta.")
        except Exception as e:
            respuesta = f"Error comunicando con el API: {e}"
    # Agrega la respuesta del bot al historial
    history.append({"role": "assistant", "content": ""})
    # Escribe lentamente la respuesta (efecto typing)
    for char in respuesta:
        history[-1]["content"] += char
        yield history

with gr.Blocks() as demo:
    chatbot = gr.Chatbot([], elem_id="chatbot", height=750, type="messages")

    with gr.Row():
        with gr.Column(scale=3):
            txt = gr.Textbox(
                show_label=False,
                placeholder="Escribe tu pregunta sobre el archivo PDF...",
                container=False
            )
        with gr.Column(scale=1, min_width=0):
            btn = gr.UploadButton("📁 Subir Archivo PDF", file_types=[".pdf"])

    txt_msg = txt.submit(
        fn=add_text,
        inputs=[chatbot, txt],
        outputs=[chatbot, txt],
        queue=False
    ).success(
        fn=bot,
        inputs=chatbot,
        outputs=chatbot
    )

    txt_msg.success(
        fn=lambda: gr.update(interactive=True),
        inputs=None,
        outputs=[txt],
        queue=False
    )

    btn.upload(
        fn=add_file,
        inputs=[chatbot, btn],
        outputs=[chatbot],
        queue=False
    )

demo.queue()

if __name__ == "__main__":
    demo.launch()
