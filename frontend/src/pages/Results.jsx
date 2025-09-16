import { useLocation, useNavigate } from "react-router-dom";
import { useHistoricalSummary } from "../api";
import { useState } from "react";

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

    const { fetchHistorical, data: historicalData, error: historicalError } = useHistoricalSummary();

    // Initialize selectedFeatures dynamically based on data.features
    const initialSelectedFeatures = Object.fromEntries(
    Object.keys(data.features).map(key => [
        key,
        key === "Make" || key === "Model" ? data.features[key] : null
    ])
);

    const [selectedFeatures, setSelectedFeatures] = useState(initialSelectedFeatures);

    function getOrdinal(n) {
        const j = n % 10,
            k = n % 100;
        if (j === 1 && k !== 11) return n + "st";
        if (j === 2 && k !== 12) return n + "nd";
        if (j === 3 && k !== 13) return n + "rd";
        return n + "th";
    }

    return (
        <div className="MainPage">
            {error && <p>{error}</p>}
            {data && (
                <div>
                    <h2>Prediction Results</h2>
                    <h3>Predicted Price: ${data.prediction.toFixed(2)}</h3>

                    {data.plots.shap_png && (
                        <div>
                            <h4>SHAP Values</h4>
                            <img src={`data:image/png;base64,${data.plots.shap_png}`} alt="SHAP"style={{ width: "800px", height: "auto" }}/>
                        </div>
                    )}
                    <h2>Historical Comparison of {data.model} Services for {data.features.Model}</h2>
                    <div>
                        <h4>Filter Historical Data</h4>

                        {Object.entries(data.features)
                            .filter(([key, value]) => value !== null && value !== undefined && key !== "Make" && key !== "Model")
                            .map(([key, value]) => (
                                <label key={key} className="block">
                                    <input
                                        type="checkbox"
                                        checked={selectedFeatures[key] !== null}
                                        onChange={() =>
                                            setSelectedFeatures(prev => ({
                                                ...prev,
                                                [key]: prev[key] !== null ? null : value
                                            }))
                                        }
                                    />
                                    {key} ({value})
                                </label>
                            ))
                        }

                        <button
                            onClick={() => {
                                if (data.prediction != null) {
                                    fetchHistorical(data.model, selectedFeatures, data.prediction);
                                } else {
                                    console.error("Prediction is missing, cannot fetch historical data.");
                                }
                            }}
                        >
                            Apply Filters
                        </button>
                    </div>

                    {historicalError && <p>{historicalError}</p>}

                    {historicalData && (
                        <div>
                            <h4>Filtered Historical Summary</h4>
                            {historicalData.summary && (
                                <div>
                                    <p>Median: ${historicalData.summary.median.toFixed(2)}</p>
                                    <p>Min: ${historicalData.summary.min.toFixed(2)}</p>
                                    <p>Max: ${historicalData.summary.max.toFixed(2)}</p>
                                </div>
                            )}
                            {historicalData.comparison && (
                                <div>

                                    <p>{historicalData.comparison.confidence} confidence as the prediction falls in the {getOrdinal(Math.round(historicalData.comparison.percentile * 100))} percentile</p>
                                </div>

                            )}

                            {historicalData.plots?.boxplot_png && (
                                <img
                                    src={`data:image/png;base64,${historicalData.plots.boxplot_png}`}
                                    alt="Boxplot"
                                />
                            )}

                            {historicalData.plots?.histogram_png && (
                                <img
                                    src={`data:image/png;base64,${historicalData.plots.histogram_png}`}
                                    alt="Histogram"
                                />
                            )}
                        </div>
                    )}

                    <button onClick={() => navigate("/")}>Make Another Prediction</button>
                </div>
            )}
        </div>
    );
}
