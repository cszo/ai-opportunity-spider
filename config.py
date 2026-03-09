import os
from dotenv import load_dotenv

load_dotenv()

ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY") or os.getenv("OPENAI_API_KEY", "")
ZHIPU_MODEL = os.getenv("ZHIPU_MODEL") or os.getenv("OPENAI_MODEL", "glm-4")
ZHIPU_BASE_URL = (
    os.getenv("ZHIPU_BASE_URL")
    or os.getenv("OPENAI_BASE_URL")
    or "https://open.bigmodel.cn/api/paas/v4/"
)

AI_KEYWORDS = [
    "ai", "llm", "gpt", "agent", "copilot", "rag", "embedding",
    "fine-tune", "finetune", "transformer", "diffusion", "generative",
    "machine learning", "deep learning", "neural", "nlp",
    "large language model", "chatbot", "openai", "anthropic", "claude",
    "stable diffusion", "midjourney", "langchain", "vector database",
    "multimodal", "vision model", "text-to", "speech-to",
    "autonomous", "reasoning", "inference", "mcp", "model context protocol",
]

REPORTS_DIR = "reports"

HN_TOP_STORIES_LIMIT = 80
GITHUB_TRENDING_URL = "https://github.com/trending?since=daily"
PRODUCTHUNT_URL = "https://www.producthunt.com"

TOP_OPPORTUNITIES_COUNT = 3
