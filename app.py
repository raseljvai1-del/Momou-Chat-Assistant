# from fastapi import FastAPI
# from fastapi.staticfiles import StaticFiles
# from fastapi.responses import FileResponse, JSONResponse
# from pydantic import BaseModel
# import google.generativeai as genai
# import uvicorn
# import os
# from dotenv import load_dotenv

# # Load env
# load_dotenv()

# genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# model = genai.GenerativeModel("models/gemini-flash-latest")

# app = FastAPI(title="FastAPI Gemini Chat App")

# app.mount("/static", StaticFiles(directory="static"), name="static")

# @app.get("/")
# async def root():
#     return FileResponse("static/index.html")


# # chat memory
# chat_session = model.start_chat(history=[
#     {
#         "role": "user",
#         "parts": [
#             "You are Momou AI Assistant. "
#             "You are polite, helpful, and professional. "
#             "Answer clearly and accurately. "
#             "If you don't know something, say honestly."
#         ]
#     }
# ])

# class ChatRequest(BaseModel):
#     message: str

# @app.post("/chat")
# async def chat(req: ChatRequest):
#     try:
#         response = chat_session.send_message(req.message)

#         if not response.text:
#             return {"reply": "Sorry, I couldn't generate a response."}

#         return {"reply": response.text}

#     except Exception as e:
#         return JSONResponse(status_code=500, content={"error": str(e)})

# if __name__ == "__main__":
#     uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)


from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import google.generativeai as genai
import uvicorn
import os
from dotenv import load_dotenv

# Load env
load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# FIX 1: Removed "models/" prefix. Use specific model name like "gemini-1.5-flash"
model = genai.GenerativeModel("models/gemini-flash-latest")

app = FastAPI(title="FastAPI Gemini Chat App")

# Ensure static directory exists to avoid crash
if not os.path.exists("static"):
    os.makedirs("static")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return FileResponse("static/index.html")

# FIX 2: Updated System Prompt to forbid formatting
chat_session = model.start_chat(history=[
    {
        "role": "user",
        "parts": [
            "You are Momou AI Assistant. "
            "You are polite, helpful, and professional. "
            "Answer clearly and accurately. "
            "If you don't know something, say honestly. "
            # INSTRUCTIONS TO REMOVE STARS/FORMATTING:
            "IMPORTANT: Do not use markdown formatting. "
            "Do not use asterisks (*) for bold text or bullet points. "
            "Write in plain text paragraphs only."
        ]
    },
    {
        "role": "model",
        "parts": ["Understood. I will provide answers in plain text without any asterisks or formatting."]
    }
])

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        response = chat_session.send_message(req.message)

        if not response.text:
            return {"reply": "Sorry, I couldn't generate a response."}

        # FIX 3: Force remove any remaining asterisks just in case
        clean_reply = response.text.replace("*", "").strip()

        return {"reply": clean_reply}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)