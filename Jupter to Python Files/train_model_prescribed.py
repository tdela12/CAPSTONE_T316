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
df = pd.read_csv('data/preprocessed_prescribed_data.csv')
df = df[df['Label'] == 1]

# %% [markdown]
# ## Grouping / Dropping Rare Tasks 
# - Decision must be made here to either drop rare tasks completely or group into a rare category.
# - Lots of variance so grouping is probably not a good idea 

# %%
task_counts = df['TaskName'].value_counts()

# Define a threshold 
threshold = 100
rare_tasks = task_counts[task_counts < threshold].index


print(len(df['TaskName'].unique()))

# Group rare tasks 
#df['TaskName'] = df['TaskName'].replace(rare_tasks, 'Other')

# Drop rare tasks
df = df[~df['TaskName'].isin(rare_tasks)].copy()

print(len(df['TaskName'].unique()))

# %% [markdown]
# ## Grouping / Dropping Rare Models

# %%
task_counts = df['Model'].value_counts()

# Define a threshold 
threshold = 20
rare_tasks = task_counts[task_counts < threshold].index


print(len(df['Model'].unique()))

# Group rare models 
#df['TaskName'] = df['TaskName'].replace(rare_tasks, 'Other')

# Drop rare models
df = df[~df['Model'].isin(rare_tasks)].copy()

print(len(df['Model'].unique()))

df.drop(columns=['Label', 'TaskName', 'Odometer', 'IsHybrid'], inplace=True)
df.head()



# %%
X = df.drop(columns=["AdjustedPrice"])  
y = df["AdjustedPrice"]     
cat_feature_indices = [0, 1, 3, 5, 6]  

# %%
X_train, X_temp, y_train, y_temp = train_test_split(
    X, y, test_size=0.3, random_state=42
)
X_test, X_val, y_test, y_val = train_test_split(
    X_temp, y_temp, test_size=0.5, random_state=42
)

# %%
for col in X_train.select_dtypes(include='object').columns:
     X_train[col] = X_train[col].fillna("missing")

for col in X_val.select_dtypes(include='object').columns:
   X_val[col] = X_val[col].fillna("missing")

for col in X_test.select_dtypes(include='object').columns:
   X_test[col] = X_test[col].fillna("missing")

# %%
def mean_absolute_percentage_error(y_true, y_pred):
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    # Avoid division by zero
    nonzero_mask = y_true != 0
    return np.mean(np.abs((y_true[nonzero_mask] - y_pred[nonzero_mask]) / y_true[nonzero_mask])) * 100

# %%
model = CatBoostRegressor(
    eval_metric='MAPE',
    loss_function='RMSEWithUncertainty',
    od_type='Iter',
    od_wait=50,
    random_seed=42,
    verbose=0,
    thread_count=4
)

param_grid = {
    'depth': [6, 8, 10],
    'learning_rate': [0.01, 0.03, 0.05, 0.1],
    'l2_leaf_reg': [1, 3, 5, 7],
    'iterations': [1000, 1500],
    'subsample': [0.8, 0.9, 1.0],
    'colsample_bylevel': [0.8, 0.9, 1.0],
    'min_child_samples': [5, 10, 20],
}


random_search = RandomizedSearchCV(
    model,
    param_distributions=param_grid,
    n_iter=25,            
    cv=3,                 
    scoring='neg_mean_absolute_percentage_error',
    random_state=42,
    verbose=2,
    n_jobs=-1
)

# %%
random_search.fit(
    X_train, y_train,
    cat_features=cat_feature_indices,
    early_stopping_rounds=200
)

print("Best params:", random_search.best_params_)
print("Best CV score (MAPE):", -random_search.best_score_)

# %%
best_params = random_search.best_params_

best_model = CatBoostRegressor(
    **best_params,
    cat_features=cat_feature_indices,
    eval_metric='MAPE',
    random_seed=42,
    verbose=100
)

best_model.fit(
    X_train, y_train,
    eval_set=(X_val, y_val),
    use_best_model=True,
    early_stopping_rounds=200
)

# %%
y_pred = best_model.predict(X_test)
print("MAE:", mean_absolute_error(y_test, y_pred))
print("RMSE:", np.sqrt(mean_squared_error(y_test, y_pred)))
mape = mean_absolute_percentage_error(y_test, y_pred)
print(f"MAPE: {mape:.2f}%")

# %%
evals_result = best_model.get_evals_result()

# Plot loss curves
plt.figure(figsize=(8,5))
plt.plot(evals_result['learn']['RMSE'], label='Training loss')
plt.plot(evals_result['validation']['RMSE'], label='Validation loss')
plt.xlabel('Iterations')
plt.ylabel('RMSE')
plt.legend()
plt.title('Training vs Validation Loss')
plt.show()

# %%
residuals = y_test - y_pred
plt.figure(figsize=(8,6))
plt.scatter(y_pred, residuals, alpha=0.5)
plt.axhline(0, color='red', linestyle='--')
plt.xlabel("Predicted Price")
plt.ylabel("Residual (Actual - Predicted)")
plt.title("Residual Plot")
plt.show()

# %%
plt.figure(figsize=(8,6))
plt.hist(residuals, bins=50, edgecolor='k', alpha=0.7)
plt.axvline(0, color='red', linestyle='--')
plt.xlabel("Error")
plt.ylabel("Frequency")
plt.title("Distribution of Prediction Errors")
plt.show()

# %%
importance = best_model.get_feature_importance()
feature_names = X_train.columns  # or your list of feature names

plt.figure(figsize=(10,6))
plt.barh(feature_names, importance)
plt.xlabel('Feature Importance')
plt.title('CatBoost Feature Importance')
plt.show()

# %%
import shap

explainer = shap.TreeExplainer(best_model)
shap_values = explainer.shap_values(X_test)

shap.summary_plot(shap_values, X_test)

# %%
best_model.save_model('models/prescribed_model.cbm')


