import sys
from pathlib import Path
import uvicorn

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

if __name__ == "__main__":
    print("Starting AI College Learning Assistant Backend from backend directory at http://127.0.0.1:8000 ...")
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True, app_dir=str(root_dir))
