import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI()

# تهيئة عميل OpenAI للاتصال بـ Hugging Face Router
client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=os.getenv("HF_TOKEN"),
)

# نموذج البيانات القادم من الواجهة
class ChatRequest(BaseModel):
    message: str

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """قراءة وعرض واجهة المستخدم index.html عند فتح الرابط الأساسي"""
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    return "index.html file not found on server!"

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        user_msg = request.message.strip()
        
        # قائمة شاملة جداً للكلمات المفتاحية بالعربية والإنجليزية لضمان الرد بدقة على أي جهاز
        creator_keywords = [
            "من صنعك", "من بنّاك", "من كتبك", "من صممك", "من خلاك", "من برمجك", "من أنشأك", "من هو مطورك", "من مالكك",
            "who created you", "who built you", "who made you", "who developed you", "your creator", "your developer"
        ]
        
        user_msg_lower = user_msg.lower()
        is_asking_creator = any(kw in user_msg_lower for kw in creator_keywords)
        
        if is_asking_creator:
            return {"reply": "تم إنشائي وبنائي بواسطة عمي وعم عيالي عبدالرحمن"}

        # الرد الطبيعي باستخدام نموذج Qwen
        response = client.chat.completions.create(
            model="Qwen/Qwen2.5-72B-Instruct",
            messages=[
                {"role": "system", "content": "أنت مساعد ذكي ومفيد للاستخدامات اليومية. أجب بشكل دقيق وودود."},
                {"role": "user", "content": user_msg}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        reply = response.choices[0].message.content
        return {"reply": reply}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))