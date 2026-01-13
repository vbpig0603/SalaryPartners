import dspy
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Config(BaseSettings):
    """
    全域設定檔 (Singleton 概念)
    自動讀取 .env，並負責初始化 DSPy
    """
    # 定義環境變數 (Pydantic 會自動轉型並檢查)
    LLM_PROVIDER: str = Field(default="gemini", description="gemini / openai / local")
    
    # Optional: 因為可能用 local 就不需要 key
    GOOGLE_API_KEY: str | None = None
    OPENAI_API_KEY: str | None = None
    
    # DSPy 參數
    DSPY_MAX_TOKENS: int = 8192
    
    # 載入 .env
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    def initialize_dspy(self):
        """根據設定初始化 DSPy (取代原本的 init_dspy 函式)"""
        lm = None
        
        if self.LLM_PROVIDER == "local":
            print("🚀 SalaryPartners running on Local Engine (Ollama)")
            lm = dspy.OllamaLocal(
                model='qwen2.5-coder', 
                max_tokens=2000,
                model_type='chat'
            )
            
        elif self.LLM_PROVIDER == "openai":
            print("💰 SalaryPartners running on OpenAI (GPT-4o)")
            if not self.OPENAI_API_KEY:
                raise ValueError("❌ 找不到 OPENAI_API_KEY，請檢查 .env")
                
            lm = dspy.LM(
                model='openai/gpt-4o',
                api_key=self.OPENAI_API_KEY,
                max_tokens=2000
            )
            
        elif self.LLM_PROVIDER == "gemini":
            print("✨ SalaryPartners running on Google Gemini 3.0 Flash (Preview)")
            if not self.GOOGLE_API_KEY:
                raise ValueError("❌ 找不到 GOOGLE_API_KEY，請檢查 .env")
            
            lm = dspy.LM(
                model='gemini/gemini-3-flash-preview', 
                api_key=self.GOOGLE_API_KEY,
                max_tokens=self.DSPY_MAX_TOKENS,
                temperature=0.0
            )
        else:
            raise ValueError(f"Unknown provider: {self.LLM_PROVIDER}")

        # 啟動 DSPy
        dspy.configure(lm=lm)

# 為了方便其他模組使用，這裡可以直接實例化一個單例
# 但如果你希望 main.py 擁有完全控制權，也可以不在這裡實例化
# 這裡遵循 Python 常見模式：
config = Config()