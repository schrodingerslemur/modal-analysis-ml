import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import "./FileUpload.css";

function FileUpload() {
  const [datFile, setDatFile] = useState(null);
  const [inpFile, setInpFile] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [dragOver, setDragOver] = useState({ dat: false, inp: false });
  const navigate = useNavigate();

  const handleFileChange = (e, fileType) => {
    const file = e.target.files[0];
    if (fileType === "dat") {
      setDatFile(file);
    } else {
      setInpFile(file);
    }
  };

  const handleDrop = (e, fileType) => {
    e.preventDefault();
    e.stopPropagation();

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      const file = files[0];
      if (fileType === "dat") {
        setDatFile(file);
      } else {
        setInpFile(file);
      }
    }

    setDragOver({ ...dragOver, [fileType]: false });
  };

  const handleDragOver = (e, fileType) => {
    e.preventDefault();
    e.stopPropagation();
    setDragOver({ ...dragOver, [fileType]: true });
  };

  const handleDragLeave = (e, fileType) => {
    e.preventDefault();
    e.stopPropagation();
    setDragOver({ ...dragOver, [fileType]: false });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!datFile || !inpFile) {
      alert("Please upload both DAT and INP files");
      return;
    }

    setIsProcessing(true);

    const formData = new FormData();
    formData.append("dat_file", datFile);
    formData.append("inp_file", inpFile);

    try {
      const response = await axios.post("/predict", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      // Navigate to results page with the response data
      navigate("/results", { state: { results: response.data } });
    } catch (error) {
      console.error("Error uploading files:", error);
      alert("Error processing files. Please try again.");
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="file-upload-container">
      <div className="main-container">
        <h5 className="app-title">Brake Rotor Mode Identification</h5>
        <p className="app-subtitle">
          Upload your rotor data files for modal analysis
        </p>

        <form onSubmit={handleSubmit} className="upload-form">
          <div className="form-group">
            <label className="form-label">📊 DAT File (Displacements)</label>
            <div
              className={`file-input-wrapper ${
                datFile ? "file-selected" : ""
              } ${dragOver.dat ? "drag-over" : ""}`}
              onDrop={(e) => handleDrop(e, "dat")}
              onDragOver={(e) => handleDragOver(e, "dat")}
              onDragLeave={(e) => handleDragLeave(e, "dat")}
            >
              <input
                type="file"
                accept=".dat"
                onChange={(e) => handleFileChange(e, "dat")}
                className="file-input"
                required
              />
              <div className="file-input-text">
                {datFile ? datFile.name : "Choose DAT file or drag & drop here"}
              </div>
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">📍 INP File (Positions)</label>
            <div
              className={`file-input-wrapper ${
                inpFile ? "file-selected" : ""
              } ${dragOver.inp ? "drag-over" : ""}`}
              onDrop={(e) => handleDrop(e, "inp")}
              onDragOver={(e) => handleDragOver(e, "inp")}
              onDragLeave={(e) => handleDragLeave(e, "inp")}
            >
              <input
                type="file"
                accept=".inp"
                onChange={(e) => handleFileChange(e, "inp")}
                className="file-input"
                required
              />
              <div className="file-input-text">
                {inpFile ? inpFile.name : "Choose INP file or drag & drop here"}
              </div>
            </div>
          </div>

          <button
            type="submit"
            className="submit-btn"
            disabled={isProcessing || !datFile || !inpFile}
          >
            {isProcessing ? "🔄 Processing..." : "🚀 Analyze Rotor Data"}
          </button>

          {isProcessing && (
            <div className="processing-indicator">
              <div className="spinner-icon"></div>
              Processing your files, please wait...
            </div>
          )}
        </form>
      </div>
    </div>
  );
}

export default FileUpload;
