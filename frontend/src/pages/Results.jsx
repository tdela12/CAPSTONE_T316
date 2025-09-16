import { useLocation, useNavigate } from "react-router-dom";

export default function ResultsPage() {
  const location = useLocation();
  const navigate = useNavigate();

  if (!location.state) {
    return (
      <div>
        <p>No prediction available. Please submit a request first.</p>
        <button onClick={() => navigate("/")}>Go Back</button>
      </div>
    );
  }

  const { data, error } = location.state;

  return (
    <div className="MainPage">
      {error && <p>{error}</p>}
      {data && (
        <div>
          <h2>Prediction Results</h2>
          <h3>Predicted Price: ${data.prediction.toFixed(2)} </h3>
          <h3>Visualisation</h3>
          {data.plots.shap_png && (
            <div>
              <h4>SHAP Values</h4>
              <img
                src={`data:image/png;base64,${data.plots.shap_png}`} 
                ></img>
            </div>)}
            {data.plots.boxplot_png && (
            <div>
              <h4>Historical Price Distribution</h4>
              <img
                src={`data:image/png;base64,${data.plots.boxplot_png}`} 
                ></img>
            </div>)}
          {data.message && <p>{data.message}</p>}
          <pre>{JSON.stringify(data, null, 2)}</pre>
          <button onClick={() => navigate("/")}>Make Another Prediction</button>
        </div>
        )}
    </div>
  );
}
