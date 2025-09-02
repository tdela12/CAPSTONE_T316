
import { BrowserRouter, Routes, Route } from "react-router-dom";
import './styling/App.css';
import Home from "./pages/Home.jsx";



function App() {
  return (
    <BrowserRouter>
      <div className='App'>
        <Routes>
          <Route path = "/" element ={<Home />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
