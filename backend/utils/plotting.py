from catboost import Pool
import matplotlib.pyplot as plt
import io
import base64
import shap

def fig_to_base64(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")

def generate_shap_plot(model, processed, feature_names):
    categorical_set = {"TaskName", "DriveType", "Make", "Model", "FuelType", "Transmission"}
    cat_features = [f for f in feature_names if f in categorical_set]

    shap_values = model.get_feature_importance(
        Pool(processed, feature_names=feature_names, cat_features=cat_features),
        type="ShapValues"
    )

    shap_values_matrix = shap_values[:, :-1]  
    expected_value = shap_values[:, -1][0]

    explainer = shap.Explanation(
        values=shap_values_matrix[0],
        base_values=expected_value,
        data=processed[0],
        feature_names=feature_names,
    )

    plt.figure()
    shap.plots.waterfall(explainer, show=False)

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")

def get_all_price_plots(filtered_df, predicted_price, month_value=None, distance_value=None, price_col="AdjustedPrice"):
    plots = {}

    # Boxplot
    fig1, ax1 = plt.subplots(figsize=(6, 4))
    ax1.boxplot(filtered_df[price_col].dropna(), vert=False, patch_artist=True,
                boxprops=dict(facecolor='lightblue'))
    ax1.axvline(predicted_price, color='red', linestyle='--', label='Predicted')
    ax1.set_title("Historical Price Distribution (Boxplot)")
    ax1.set_xlabel("Price")
    ax1.legend()
    plots["boxplot_png"] = fig_to_base64(fig1)
    plt.close(fig1)

    # Histogram
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.hist(filtered_df[price_col].dropna(), bins=20, edgecolor='black', alpha=0.7)
    ax2.axvline(predicted_price, color='red', linestyle='--', label='Predicted')
    ax2.set_title("Historical Price Distribution (Histogram)")
    ax2.set_xlabel("Price")
    ax2.set_ylabel("Frequency")
    ax2.legend()
    plots["histogram_png"] = fig_to_base64(fig2)
    plt.close(fig2)

    # Months vs Price
    if "Months" in filtered_df.columns:
        fig3, ax3 = plt.subplots(figsize=(6,4))
        ax3.scatter(filtered_df["Months"], filtered_df[price_col], alpha=0.6, label="Historical")
        if month_value is not None:
            ax3.scatter([month_value], [predicted_price], color="red", s=100, label="Predicted", zorder=5)
        ax3.set_xlabel("Months")
        ax3.set_ylabel("Price")
        ax3.set_title("Price vs Months")
        ax3.legend()
        plots["month_vs_price_png"] = fig_to_base64(fig3)
        plt.close(fig3)
    
    # Distance vs Price
    if "Distance" in filtered_df.columns:
        fig4, ax4 = plt.subplots(figsize=(6,4))
        ax4.scatter(filtered_df["Distance"], filtered_df[price_col], alpha=0.6, label="Historical")
        if distance_value is not None:
            ax4.scatter([distance_value], [predicted_price], color="red", s=100, label="Predicted", zorder=5)
        ax4.set_xlabel("Distance")
        ax4.set_ylabel("Price")
        ax4.set_title("Price vs Distance")
        ax4.legend()
        plots["distance_vs_price_png"] = fig_to_base64(fig4)
        plt.close(fig4)

    return plots
