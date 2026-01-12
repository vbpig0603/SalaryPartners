import dspy
import os
from dotenv import load_dotenv

# 強制載入 .env，無論是從哪裡執行 uv run
load_dotenv(override=True)

def init_dspy(provider="gemini"): # 預設改用 gemini
    
    lm = None
    
    if provider == "local":
        # --- 本機 Ollama ---
        print("🚀 SalaryPartners running on Local Engine (Ollama)")
        # 注意：本地端通常還是可以用 OllamaLocal，或者也可以改用 dspy.LM('ollama/qwen2.5-coder')
        lm = dspy.OllamaLocal(
            model='qwen2.5-coder', 
            max_tokens=2000,
            model_type='chat'
        )
        
    elif provider == "openai":
        # --- OpenAI GPT-4o ---
        print("💰 SalaryPartners running on OpenAI (GPT-4o)")
        api_key = os.getenv("OPENAI_API_KEY")
        
        # ✅ 新版寫法：使用 dspy.LM
        lm = dspy.LM(
            model='openai/gpt-4o',
            api_key=api_key,
            max_tokens=2000
        )
        
    elif provider == "gemini":
        # --- Google Gemini ---
        print("✨ SalaryPartners running on Google Gemini 1.5 Flash")
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("❌ 找不到 GOOGLE_API_KEY，請檢查 .env")
        
        # ✅ 修改點：改用 "gemini-1.5-flash-latest" 或 "gemini-1.5-flash-001"
        # 這樣 litellm 比較容易對應到正確的 Google API 端點
        lm = dspy.LM(
            model='gemini/gemini-3-flash-preview', 
            api_key=api_key,
            max_tokens=8192,
            temperature=0.0
        )

    else:
        raise ValueError(f"Unknown provider: {provider}")

    dspy.configure(lm=lm)