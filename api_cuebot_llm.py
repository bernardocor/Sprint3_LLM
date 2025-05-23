
from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
import uvicorn
import os

# Obtiene la clave desde la variable de entorno OPENAI_API_KEY
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Debes definir la variable de entorno OPENAI_API_KEY con tu clave de OpenAI.")

client = OpenAI(api_key=api_key)

app = FastAPI()

class LLMRequest(BaseModel):
    instruccion: str
    texto: str

@app.post("/cuebot/")
async def cuebot_llm(req: LLMRequest):
    '''
    Endpoint que recibe una instrucción y un texto,
    y devuelve la respuesta generada por un LLM en español.
    '''
    prompt = (
        f"Instrucción: {req.instruccion}\n"
        f"Texto a analizar:\n{req.texto}\n"
        "Responde únicamente en español."
    )

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Eres un experto analizando textos académicos y respondiendo en español."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=700
    )
    return {"respuesta": response.choices[0].message.content.strip()}

# Para ejecutar localmente: uvicorn api_cuebot_llm:app --reload
if __name__ == "__main__":
    uvicorn.run("api_cuebot_llm:app", host="0.0.0.0", port=8000, reload=True)
