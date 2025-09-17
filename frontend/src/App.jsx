
import { BrowserRouter, Routes, Route } from "react-router-dom";
import './styling/App.css';
import DataEntry from "./pages/DataEntry.jsx";
import Results from "./pages/Results.jsx";



function App() {
  return (
    <BrowserRouter>
      <div className='App'>
        <Routes>
          <Route path = "/" element ={<DataEntry />} />
          <Route path = "/results" element ={<Results />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
