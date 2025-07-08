import os
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse

from backend.routes import register_routes

# compute project_root/
BASE = Path(__file__).parent.parent.absolute()

# where to save uploads
UPLOAD_DIR = Path(os.environ.get("UPLOAD_FOLDER", "/tmp/uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Your API", version="1.0.0")

# Store upload directory in app state for access in routes
app.state.upload_folder = UPLOAD_DIR

# register routes
register_routes(app)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5000)
