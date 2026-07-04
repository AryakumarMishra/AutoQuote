import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    dashscope_api_key: str = os.environ.get("DASHSCOPE_API_KEY", "")
    qwen_base_url: str = os.environ.get(
        "QWEN_BASE_URL", "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
    )
    model_parse: str = os.environ.get("QWEN_MODEL_PARSE", "qwen-turbo")
    model_sanitize: str = os.environ.get("QWEN_MODEL_SANITIZE", "qwen-turbo")
    model_risk: str = os.environ.get("QWEN_MODEL_RISK", "qwen-plus")
    mock_mode: bool = os.environ.get("MOCK_MODE", "true").lower() == "true"
    high_value_threshold_usd: float = float(
        os.environ.get("HIGH_VALUE_THRESHOLD_USD", "2000")
    )


settings = Settings()