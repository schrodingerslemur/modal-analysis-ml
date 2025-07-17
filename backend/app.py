import os
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from backend.routes import register_routes

# compute project_root/
BASE = Path(__file__).parent.parent.absolute()

# where to save uploads
UPLOAD_DIR = Path(os.environ.get("UPLOAD_FOLDER", "/tmp/uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Modal Analysis API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store upload directory in app state for access in routes
app.state.upload_folder = UPLOAD_DIR

# register routes
register_routes(app)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5000)
