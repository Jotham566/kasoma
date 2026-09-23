from services.config import Settings
from services.providers import MinioObjectStorage

MinioObjectStorage(Settings()).ensure_container()
print("Local object-storage container ready (private by default).")
