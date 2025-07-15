import { useLocation, useNavigate } from "react-router-dom";
import { useEffect } from "react";
import "./Results.css";

function Results() {
  const location = useLocation();
  const navigate = useNavigate();
  const results = location.state?.results;

  useEffect(() => {
    if (!results) {
      navigate("/");
      return;
    }

    // Apply cell highlighting after component mounts
    const timer = setTimeout(() => {
      const table = document.querySelector("table.results-table");
      if (!table) return;

      const headers = Array.from(table.querySelectorAll("thead th"));
      const lowerIdx = headers.findIndex(
        (h) => h.textContent.trim() === "Lower Frequency Diff (Hz)"
      );
      const upperIdx = headers.findIndex(
        (h) => h.textContent.trim() === "Upper Frequency Diff (Hz)"
      );

      table.querySelectorAll("tbody tr").forEach((row) => {
        const cells = row.querySelectorAll("td");

        [lowerIdx, upperIdx].forEach((idx) => {
          if (idx < 0) return;

          const val = cells[idx]?.textContent.trim();
          const num =
            val === "" || val.toLowerCase() === "nan" ? NaN : parseFloat(val);

          if (cells[idx]) {
            if (isNaN(num) || num <= 300) {
              cells[idx].classList.add("highlight-red");
            } else {
              cells[idx].classList.add("highlight-green");
            }
          }
        });
      });
    }, 100);

    return () => clearTimeout(timer);
  }, [results, navigate]);

  if (!results) {
    return (
      <div className="results-container">
        <div className="container">
          <div className="alert alert-danger">
            No results to display. Please go back and upload files.
          </div>
          <button onClick={() => navigate("/")} className="btn btn-primary">
            Back to Upload
          </button>
        </div>
      </div>
    );
  }

  const renderTable = () => {
    if (!results.results || results.results.length === 0) {
      return <p>No results to display.</p>;
    }

    const headers = Object.keys(results.results[0]);

    return (
      <div className="table-responsive">
        <table className="results-table table">
          <thead>
            <tr>
              {headers.map((header, index) => (
                <th key={index}>{header}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {results.results.map((row, index) => (
              <tr key={index}>
                {headers.map((header, cellIndex) => (
                  <td key={cellIndex}>
                    {row[header] !== null && row[header] !== undefined
                      ? typeof row[header] === "number"
                        ? row[header].toFixed(2)
                        : row[header]
                      : "NaN"}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  return (
    <div className="results-container">
      <div className="container">
        <h1>Modal Identification Results</h1>

        {results.modal_target && (
          <p>
            <strong>Modal Separation Target: </strong>
            <span
              className={
                results.modal_target === "Met" ? "text-success" : "text-danger"
              }
            >
              {results.modal_target}
            </span>
          </p>
        )}

        {results.inplane_modes && (
          <p>
            <strong>Inplane Modes: </strong>{" "}
            {Array.isArray(results.inplane_modes)
              ? results.inplane_modes.join(", ")
              : results.inplane_modes}
          </p>
        )}

        {results.out_of_plane_modes && (
          <p>
            <strong>Out-of-plane Modes: </strong>{" "}
            {Array.isArray(results.out_of_plane_modes)
              ? results.out_of_plane_modes.join(", ")
              : results.out_of_plane_modes}
          </p>
        )}

        {renderTable()}

        <button onClick={() => navigate("/")} className="btn btn-primary mt-3">
          Back to Upload
        </button>
      </div>
    </div>
  );
}

export default Results;
