import os
from pathlib import Path
from typing import Dict, Any

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse

from scripts.main import main


def register_routes(app: FastAPI):
    @app.post("/predict")
    async def predict(
        dat_file: UploadFile = File(..., description="DAT file upload"),
        inp_file: UploadFile = File(..., description="INP file upload"),
    ) -> Dict[str, Any]:
        # Validate file uploads
        if not dat_file.filename or not inp_file.filename:
            raise HTTPException(
                status_code=400, detail="Please upload both dat_file and inp_file"
            )

        # Get upload directory from app state
        upload_dir = app.state.upload_folder

        # Create secure file paths
        dat_path = upload_dir / dat_file.filename
        inp_path = upload_dir / inp_file.filename

        try:
            # Save uploaded files
            with open(dat_path, "wb") as f:
                content = await dat_file.read()
                f.write(content)

            with open(inp_path, "wb") as f:
                content = await inp_file.read()
                f.write(content)

            # Process the files
            result = main(str(dat_path), str(inp_path))

            # Convert DataFrame to dict if it exists
            response_data = {}
            if "Results" in result and hasattr(result["Results"], "to_dict"):
                response_data["results"] = result["Results"].to_dict(orient="records")

            # Add other result fields
            if "Modal Separation Target" in result:
                response_data["modal_target"] = result["Modal Separation Target"]
            if "Inplane modes" in result:
                response_data["inplane_modes"] = result["Inplane modes"]
            if "Out-of-plane modes" in result:
                response_data["out_of_plane_modes"] = result["Out-of-plane modes"]

            return response_data

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

        finally:
            # Optional: Clean up uploaded files after processing
            # dat_path.unlink(missing_ok=True)
            # inp_path.unlink(missing_ok=True)
            pass
