# %% [markdown]
# ## Import Statements

# %%
import pandas as pd
from sklearn.model_selection import train_test_split
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
from catboost import CatBoostRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error


# %% [markdown]
# ## Read in Data

# %%
df = pd.read_csv('data/preprocessed_log_data.csv')
df = df[df['Label'] == 1]
df.drop(columns=['Label', 'IsHybrid'], inplace=True) # Drop TaskName as all are 'Logbook'
df.head()

# %%
feature_name = 'FuelType'
unique_categories = df[feature_name].unique()
print(f"Categories of '{feature_name}':")
for category in unique_categories:
    print(category)

# %%
feature_name = 'Transmission'
unique_categories = df[feature_name].unique()
print(f"Categories of '{feature_name}':")
for category in unique_categories:
    print(category)

# %%
feature_name = 'DriveType'
unique_categories = df[feature_name].unique()
print(f"Categories of '{feature_name}':")
for category in unique_categories:
    print(category)

# %%
X = df.drop(columns=["AdjustedPrice"])  
y = df["AdjustedPrice"]       

# %%
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# %%
print(X_test['Model'].unique().size)

# %%
# Identify feature types
cat_features = X_train.select_dtypes(include=["object", "category"]).columns
print(cat_features)

# %%
for col in X_train.select_dtypes(include='object').columns:
     X_train[col] = X_train[col].fillna("missing")

for col in X_test.select_dtypes(include='object').columns:
     X_test[col] = X_test[col].fillna("missing")

# %%
def mean_absolute_percentage_error(y_true, y_pred):
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    # Avoid division by zero
    nonzero_mask = y_true != 0
    return np.mean(np.abs((y_true[nonzero_mask] - y_pred[nonzero_mask]) / y_true[nonzero_mask])) * 100

# %%
cat_feature_indices = [0, 1, 3, 5]

model = CatBoostRegressor(
    cat_features=cat_feature_indices,
    eval_metric='MAPE',
    od_type='Iter',
    od_wait=50,
    random_seed=42,
    verbose=100
)

model.fit(X_train, y_train, 
                  verbose=False)



# %%
y_pred = model.predict(X_test)

def top_n_accuracy(y_true, y_pred):
    
    errors = np.abs(y_true - y_pred)

    results = pd.DataFrame({
        "y_true": y_true,
        "y_pred": y_pred,
        "error": errors  })

    sorted_results = results.sort_values(by="error")
    top5_accurate = sorted_results.head(5)
    top5_inaccurate = sorted_results.tail(5)

    print("Top 5 Most Accurate Predictions:")
    print(top5_accurate)

    print("\nTop 5 Least Accurate Predictions:")
    print(top5_inaccurate)

# %%
def top_n_categories(y_true, y_pred, features_df, feature_col, top_n=5, error_type="mae"):
    
    df = pd.DataFrame({
      "y_true": y_true,
      "y_pred": y_pred,
      "error": y_true - y_pred
    })

    df[feature_col] = features_df[feature_col].values
    if error_type == "mae":
      df["err"] = df["error"].abs()


    if error_type == "mse":
      df["err"] = df["error"]**2
      


    grouped = df.groupby(feature_col).aggregate(avg_error=("err", "mean"),frequency=("err", "count"))

    sorted = grouped.sort_values("avg_error")
    best = sorted.head(top_n).reset_index()
    worst = sorted.tail(top_n).reset_index()
    
    print("Top 5 Best Categories:")
    print(best)

    print("\nTop 5 Least Accurate Predictions:")
    print(worst)      



# %%
top_n_accuracy(y_test, y_pred)
top_n_categories(y_test, y_pred, X_test, 'Model', error_type="mse")

# %%



best_model.fit(X_train, y_train)

y_pred = best_model.predict(X_test)
print("MAE:", mean_absolute_error(y_test, y_pred))
print("RMSE:", np.sqrt(mean_squared_error(y_test, y_pred)))
mape = mean_absolute_percentage_error(y_test, y_pred)
print(f"MAPE: {mape:.2f}%")


# %%
importance = best_model.get_feature_importance()
feature_names = X_train.columns  # or your list of feature names

plt.figure(figsize=(10,6))
plt.barh(feature_names, importance)
plt.xlabel('Feature Importance')
plt.title('CatBoost Feature Importance')
plt.show()


