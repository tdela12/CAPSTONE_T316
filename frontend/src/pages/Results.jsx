import { useLocation, useNavigate } from "react-router-dom";
import { useHistoricalSummary } from "../api";
import { useState } from "react";

export default function ResultsPage() {
    const location = useLocation();
    const navigate = useNavigate();

    const { fetchHistorical, data: historicalData, error: historicalError } = useHistoricalSummary();
    const [loading, setLoading] = useState(false);

    if (!location.state) {
        return (
            <div>
                <p>No prediction available. Please submit a request first.</p>
                <button onClick={() => navigate("/")}>Go Back</button>
            </div>
        );
    }

    const { data, error } = location.state;

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

    const handleFetchHistorical = async () => {
        if (data.prediction != null) {
            setLoading(true);
            await fetchHistorical(
                data.model,
                selectedFeatures,
                data.prediction,
                data.features.Months,
                data.features.Distance
            );
            setLoading(false);
        } else {
            console.error("Prediction is missing, cannot fetch historical data.");
        }
    };

    return (
        <div className="MainPage">
            {error && <p className="text-red-500">{error}</p>}

            {data && (
                <div className="resultsContainer">

                    {/* Prediction Card */}
                    <div className="card">
                        <h2 className="sectionTitle">Prediction Results</h2>
                        <p className="predictedPrice">
                            Predicted Price: <span>${data.prediction?.toFixed(2) ?? "N/A"}</span>
                        </p>
                    </div>

                    {/* Historical Filters */}
                    <div className="card">
                        <h2 className="sectionTitle">
                            Historical Comparison of {data.model} Services for {data.features.Model}
                        </h2>

                        <h4>Filter Historical Data</h4>
                        <div className="filtersGrid">
                            {Object.entries(data.features)
                                .filter(([key, value]) => value !== null && value !== undefined && key !== "Make" && key !== "Model")
                                .map(([key, value]) => (
                                    <label key={key} className="filterOption">
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
                                        {key}: <span>{value}</span>
                                    </label>
                                ))}
                        </div>

                        <button className="btnPrimary" onClick={handleFetchHistorical}>
                            Apply Filters
                        </button>
                        {loading && <p>Loading historical data...</p>}
                    </div>

                    {/* Historical Summary */}
                    {historicalData && (
                        <div className="card">
                            <h3 className="sectionTitle">Filtered Historical Summary</h3>

                            {historicalData.summary ? (
                                <div className="summaryGrid">
                                    <p><strong>Median:</strong> ${historicalData.summary.median?.toFixed(2) ?? "N/A"}</p>
                                    <p><strong>Min:</strong> ${historicalData.summary.min?.toFixed(2) ?? "N/A"}</p>
                                    <p><strong>Max:</strong> ${historicalData.summary.max?.toFixed(2) ?? "N/A"}</p>
                                    <p><strong>Count:</strong> {historicalData.summary.count ?? "No available rows"}</p>
                                </div>
                            ) : (
                                <p>No historical summary available.</p>
                            )}

                            {historicalData.comparison && (
                                <p className="confidenceText">
                                    {historicalData.comparison.confidence ?? "N/A"} confidence — falls in the{" "}
                                    {getOrdinal(Math.round((historicalData.comparison.percentile ?? 0) * 100))} percentile
                                </p>
                            )}
                        </div>
                    )}

                    {/* Historical Plots */}
                    {historicalData?.plots && (
                        <div className="plotsGrid">
                            {historicalData.plots.boxplot_png && (
                                <img src={`data:image/png;base64,${historicalData.plots.boxplot_png}`} alt="Boxplot" className="plotImg" />
                            )}
                            {historicalData.plots.histogram_png && (
                                <img src={`data:image/png;base64,${historicalData.plots.histogram_png}`} alt="Histogram" className="plotImg" />
                            )}
                            {historicalData.plots.distance_vs_price_png && (
                                <img src={`data:image/png;base64,${historicalData.plots.distance_vs_price_png}`} alt="Distance vs Price" className="plotImg" />
                            )}
                            {historicalData.plots.month_vs_price_png && (
                                <img src={`data:image/png;base64,${historicalData.plots.month_vs_price_png}`} alt="Month vs Price" className="plotImg" />
                            )}
                        </div>
                    )}

                    {/* SHAP Plot */}
                    {data.plots?.shap_png && (
                        <div className="card">
                            <h3 className="sectionTitle">Feature Importance (SHAP)</h3>
                            <img
                                src={`data:image/png;base64,${data.plots.shap_png}`}
                                alt="SHAP"
                                className="plotImg"
                            />
                        </div>
                    )}

                    {/* Navigation */}
                    <div className="formActions">
                        <button className="btnSecondary" onClick={() => navigate("/")}>
                            Make Another Prediction
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}
