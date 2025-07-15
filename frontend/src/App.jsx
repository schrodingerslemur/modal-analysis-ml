import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import FileUpload from "./components/FileUpload";
import Results from "./components/Results";
import "./App.css";

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<FileUpload />} />
          <Route path="/results" element={<Results />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
