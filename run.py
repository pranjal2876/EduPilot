import os
import sys
from pathlib import Path
import uvicorn

root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 8000))
    reload = os.environ.get("RELOAD", "false").lower() in ("true", "1")
    print(f"Starting AI College Learning Assistant Backend on {host}:{port} ...")
    uvicorn.run("backend.main:app", host=host, port=port, reload=reload, app_dir=str(root_dir))
