"""Local HTTP probe only: no inference, model download or external fallback."""

from services.config import Settings
from services.providers import OllamaConnectivity

try:
    available = OllamaConnectivity(Settings().model_base_url).available()
except Exception:
    available = False
if not available:
    raise SystemExit("Host-native Ollama is unavailable. Start it locally; no inference performed.")
print("Host-native Ollama connectivity passed. No inference performed.")
