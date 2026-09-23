import json
from pathlib import Path

from apps.api.main import create_app

path = Path("packages/api-client/openapi.json")
path.write_text(json.dumps(create_app().openapi(), indent=2, sort_keys=True) + "\n")
