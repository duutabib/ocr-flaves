from fastapi import FastAPI
import ollama

app = FastAPI()

@app.get("/generate")
def generate(prompt: str):
    response = ollama.chat(
        model="llama2",
        messages=[{"role": "user", "content": prompt}]
    )
    return {"response": response["message"]["content"]}
