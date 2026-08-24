import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
---CELL---
df = pd.read_csv('/content/transactions.csv')
df.head();
---CELL---
print('DataFrame Info:')
display(df.info())
---CELL---
print('\nDataFrame Description:')
display(df.describe())
---CELL---
print('\nNumber of duplicate rows:')
display(df.duplicated().sum())
---CELL---
print('\nNumber of missing values per column:')
display(df.isnull().sum())
---CELL---
print(f"Original DataFrame shape: {df.shape}")
df.dropna(inplace=True)
print(f"DataFrame shape after dropping missing values: {df.shape}")
print('\nNumber of missing values per column after dropping:')
display(df.isnull().sum())
---CELL---
plt.figure(figsize=(6, 4))
sns.countplot(x='recovered', data=df)
plt.title('Distribution of Target Variable (recovered)')
plt.xlabel('Recovered')
plt.ylabel('Count')
plt.show()

print('\nPercentage of recovered vs. not recovered:')
display(df['recovered'].value_counts(normalize=True))
---CELL---
plt.figure(figsize=(10, 6))
sns.countplot(y='failure_reason', data=df, order = df['failure_reason'].value_counts().index)
plt.title('Distribution of Failure Reasons')
plt.xlabel('Count')
plt.ylabel('Failure Reason')
plt.show()

print('\nPercentage of each failure reason:')
display(df['failure_reason'].value_counts(normalize=True))
---CELL---
plt.figure(figsize=(8, 5))
sns.countplot(x='payment_method', data=df, order = df['payment_method'].value_counts().index)
plt.title('Distribution of Payment Methods')
plt.xlabel('Payment Method')
plt.ylabel('Count')
plt.show()

print('\nPercentage of each payment method:')
display(df['payment_method'].value_counts(normalize=True))
---CELL---
plt.figure(figsize=(7, 5))
sns.countplot(x='retry_count', data=df)
plt.title('Distribution of Retry Count')
plt.xlabel('Retry Count')
plt.ylabel('Number of Transactions')
plt.show()

print('\nPercentage of each retry count:')
display(df['retry_count'].value_counts(normalize=True))
---CELL---
plt.figure(figsize=(10, 6))
sns.histplot(df['hours_since_failure'], bins=50, kde=True)
plt.title('Distribution of Hours Since Failure')
plt.xlabel('Hours Since Failure')
plt.ylabel('Frequency')
plt.show()

print('\nDescriptive statistics for hours since failure:')
display(df['hours_since_failure'].describe())
---CELL---
plt.figure(figsize=(10, 6))
sns.histplot(df['days_since_last_success'], bins=50, kde=True)
plt.title('Distribution of Days Since Last Success')
plt.xlabel('Days Since Last Success')
plt.ylabel('Frequency')
plt.show()

print('\nDescriptive statistics for days since last success:')
display(df['days_since_last_success'].describe())
---CELL---
df_fe = df.copy()

# Drop identifiers (transaction_id and customer_id will not be useful as features)
df_fe = df_fe.drop(columns=['transaction_id', 'customer_id'])

# Feature Engineering
df_fe['success_failure_ratio'] = df_fe['previous_successes'] / (df_fe['previous_failures'] + 1)
df_fe['total_previous_transactions'] = df_fe['previous_successes'] + df_fe['previous_failures']

print("DataFrame after dropping identifiers and adding new features:")
display(df_fe.head())
---CELL---
from sklearn.model_selection import train_test_split

# Define features (X) and target (y)
X = df_fe.drop('recovered', axis=1)
y = df_fe['recovered']

# Identify categorical and numerical columns for preprocessing
categorical_features = X.select_dtypes(include=['object']).columns
numerical_features = X.select_dtypes(include=np.number).columns

print("Categorical Features:", list(categorical_features))
print("Numerical Features:", list(numerical_features))

# Split into 70% training and 30% temporary (validation + test)
X_train, X_temp, y_train, y_temp = train_test_split(
    X, y, test_size=0.30, random_state=42, stratify=y
)

# Split temporary into 15% validation and 15% test
# (0.50 of 30% is 15%)
X_val, X_test, y_val, y_test = train_test_split(
    X_temp, y_temp, test_size=0.50, random_state=42, stratify=y_temp
)

print(f"\nTraining set shape: {X_train.shape}, {y_train.shape}")
print(f"Validation set shape: {X_val.shape}, {y_val.shape}")
print(f"Test set shape: {X_test.shape}, {y_test.shape}")

print("\nTarget distribution in Training Set:")
display(y_train.value_counts(normalize=True))

print("\nTarget distribution in Validation Set:")
display(y_val.value_counts(normalize=True))

print("\nTarget distribution in Test Set:")
display(y_test.value_counts(normalize=True))
---CELL---
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

# Define the preprocessing steps
numerical_transformer = StandardScaler()
categorical_transformer = OneHotEncoder(handle_unknown='ignore')

# Create a column transformer to apply different transformations to different columns
preprocessor = ColumnTransformer(
    transformers=[
        ('num', numerical_transformer, numerical_features),
        ('cat', categorical_transformer, categorical_features)
    ],
    remainder='passthrough' # Keep other columns not specified (if any)
)

# Fit the preprocessor only on the training data and transform all sets
X_train_processed = preprocessor.fit_transform(X_train)
X_val_processed = preprocessor.transform(X_val)
X_test_processed = preprocessor.transform(X_test)

# Get feature names after one-hot encoding
# This step needs to handle the possibility of ColumnTransformer's output not being a DataFrame
# For dense output, it's a numpy array. For sparse, it's a sparse matrix.
# We will store the feature names for later use (e.g., feature importance)

# Get numerical feature names directly
processed_numerical_feature_names = list(numerical_features)

# Get categorical feature names after OneHotEncoder
# This will vary based on the OneHotEncoder's output
processed_categorical_feature_names = list(preprocessor.named_transformers_['cat'].get_feature_names_out(categorical_features))

# Combine all feature names
all_processed_feature_names = processed_numerical_feature_names + processed_categorical_feature_names

print("Shape of processed training data:", X_train_processed.shape)
print("Shape of processed validation data:", X_val_processed.shape)
print("Shape of processed test data:", X_test_processed.shape)
print("\nFirst 5 processed feature names:", all_processed_feature_names[:5])
print("Total processed features:", len(all_processed_feature_names))
---CELL---
plt.figure(figsize=(10, 6))
sns.histplot(df['customer_lifetime_value'], bins=50, kde=True)
plt.title('Distribution of Customer Lifetime Value')
plt.xlabel('Customer Lifetime Value')
plt.ylabel('Frequency')
plt.show()

print('\nDescriptive statistics for customer lifetime value:')
display(df['customer_lifetime_value'].describe())
---CELL---
plt.figure(figsize=(10, 6))
sns.histplot(df['customer_tenure_days'], bins=50, kde=True)
plt.title('Distribution of Customer Tenure Days')
plt.xlabel('Customer Tenure Days')
plt.ylabel('Frequency')
plt.show()

print('\nDescriptive statistics for customer tenure days:')
display(df['customer_tenure_days'].describe())
---CELL---
plt.figure(figsize=(10, 6))
sns.histplot(df['payment_success_rate'], bins=30, kde=True)
plt.title('Distribution of Payment Success Rate')
plt.xlabel('Payment Success Rate')
plt.ylabel('Frequency')
plt.show()

print('\nDescriptive statistics for payment success rate:')
display(df['payment_success_rate'].describe())
---CELL---
plt.figure(figsize=(10, 6))
sns.histplot(df['amount'], bins=50, kde=True)
plt.title('Distribution of Transaction Amount')
plt.xlabel('Amount')
plt.ylabel('Frequency')
plt.show()

print('\nDescriptive statistics for amount:')
display(df['amount'].describe())
---CELL---
from sklearn.linear_model import LogisticRegression

# Initialize and train Logistic Regression model
log_reg_model = LogisticRegression(random_state=42, solver='liblinear') # Using liblinear for small datasets and L1/L2 regularization
log_reg_model.fit(X_train_processed, y_train)

print("Logistic Regression model trained successfully!")
---CELL---
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix, ConfusionMatrixDisplay

def evaluate_model(model, X_val, y_val, model_name):
    y_pred = model.predict(X_val)
    y_proba = model.predict_proba(X_val)[:, 1]

    precision = precision_score(y_val, y_pred)
    recall = recall_score(y_val, y_pred)
    f1 = f1_score(y_val, y_pred)
    roc_auc = roc_auc_score(y_val, y_proba)
    cm = confusion_matrix(y_val, y_pred)

    print(f"--- {model_name} Evaluation ---")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1 Score: {f1:.4f}")
    print(f"ROC-AUC: {roc_auc:.4f}")
    print("Confusion Matrix:")
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=[False, True])
    disp.plot(cmap=plt.cm.Blues)
    plt.title(f'Confusion Matrix for {model_name}')
    plt.show()

    return {
        'Model': model_name,
        'Precision': precision,
        'Recall': recall,
        'F1 Score': f1,
        'ROC-AUC': roc_auc,
        'Confusion Matrix': cm
    }

log_reg_metrics = evaluate_model(log_reg_model, X_val_processed, y_val, 'Logistic Regression')

# Store metrics for comparison later
model_performance = [log_reg_metrics]

---CELL---
from sklearn.ensemble import RandomForestClassifier

# Initialize and train Random Forest model
# Using a reasonable number of estimators and a fixed random state for reproducibility
rf_model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
rf_model.fit(X_train_processed, y_train)

print("Random Forest model trained successfully!")
---CELL---
rf_metrics = evaluate_model(rf_model, X_val_processed, y_val, 'Random Forest')
model_performance.append(rf_metrics)
---CELL---
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

# Convert processed numpy arrays to PyTorch tensors
X_train_tensor = torch.tensor(X_train_processed, dtype=torch.float32)
y_train_tensor = torch.tensor(y_train.values, dtype=torch.float32).unsqueeze(1)
X_val_tensor = torch.tensor(X_val_processed, dtype=torch.float32)
y_val_tensor = torch.tensor(y_val.values, dtype=torch.float32).unsqueeze(1)

# Create TensorDatasets
train_dataset = TensorDataset(X_train_tensor, y_train_tensor)
val_dataset = TensorDataset(X_val_tensor, y_val_tensor)

# Create DataLoaders
batch_size = 64
train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

# Define the MLP architecture
class MLP(nn.Module):
    def __init__(self, input_size):
        super(MLP, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(input_size, 64),
            nn.ReLU(),
            nn.Dropout(0.3), # Added dropout
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Dropout(0.3), # Added dropout
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Dropout(0.3), # Added dropout
            nn.Linear(16, 1)
            # Removed nn.Sigmoid() here. BCEWithLogitsLoss expects raw logits.
        )

    def forward(self, x):
        return self.network(x)

# Initialize the model, loss function, and optimizer
input_size = X_train_processed.shape[1]
mlp_model = MLP(input_size)

criterion = nn.BCEWithLogitsLoss() # Use BCEWithLogitsLoss for numerical stability with raw logits
optimizer = optim.Adam(mlp_model.parameters(), lr=0.001)

# Early stopping parameters
num_epochs = 100
patience = 10
best_val_loss = float('inf')
epochs_no_improve = 0

print("Training PyTorch MLP model...")

# Training loop with early stopping
for epoch in range(num_epochs):
    mlp_model.train() # Set model to training mode
    for inputs, labels in train_loader:
        optimizer.zero_grad()
        outputs = mlp_model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

    # Evaluate on validation set
    mlp_model.eval() # Set model to evaluation mode
    val_loss = 0.0
    with torch.no_grad():
        for inputs, labels in val_loader:
            outputs = mlp_model(inputs)
            val_loss += criterion(outputs, labels).item()
    val_loss /= len(val_loader)

    print(f'Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item():.4f}, Val Loss: {val_loss:.4f}')

    # Early stopping check
    if val_loss < best_val_loss:
        best_val_loss = val_loss
        epochs_no_improve = 0
        # Save the best model state
        torch.save(mlp_model.state_dict(), 'best_mlp_model.pth')
    else:
        epochs_no_improve += 1
        if epochs_no_improve == patience:
            print(f'Early stopping after {epoch+1} epochs due to no improvement in validation loss.')
            break

print("PyTorch MLP model training complete!")

# Load the best model for evaluation
mlp_model.load_state_dict(torch.load('best_mlp_model.pth'))
---CELL---
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix, ConfusionMatrixDisplay

# Evaluate PyTorch MLP model using the evaluate_model function
# First, get predictions and probabilities from the PyTorch model
mlp_model.eval()
val_preds = []
val_probs = []
with torch.no_grad():
    for inputs, _ in val_loader:
        logits = mlp_model(inputs) # Get raw logits
        probabilities = torch.sigmoid(logits) # Apply sigmoid for probabilities
        val_probs.extend(probabilities.cpu().numpy().flatten())
        val_preds.extend((probabilities.cpu().numpy().flatten() > 0.5).astype(int))

# The evaluate_model function expects numpy arrays for X and y
# We'll pass dummy X_val_processed for the function's signature, but use our gathered preds/probs
# The function expects 'model.predict' and 'model.predict_proba' which PyTorch model doesn't have directly.
# So, we'll create a dummy class or modify the evaluate_model function slightly.

# Let's adapt the evaluation function for PyTorch model output
def evaluate_pytorch_model(y_true, y_pred, y_proba, model_name):
    precision = precision_score(y_true, y_pred)
    recall = recall_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)
    roc_auc = roc_auc_score(y_true, y_proba)
    cm = confusion_matrix(y_true, y_pred)

    print(f"--- {model_name} Evaluation ---")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1 Score: {f1:.4f}")
    print(f"ROC-AUC: {roc_auc:.4f}")
    print("Confusion Matrix:")
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=[False, True])
    disp.plot(cmap=plt.cm.Blues)
    plt.title(f'Confusion Matrix for {model_name}')
    plt.show()

    return {
        'Model': model_name,
        'Precision': precision,
        'Recall': recall,
        'F1 Score': f1,
        'ROC-AUC': roc_auc,
        'Confusion Matrix': cm
    }

mlp_metrics = evaluate_pytorch_model(y_val.values, val_preds, val_probs, 'PyTorch MLP')
model_performance.append(mlp_metrics)
---CELL---
# Re-initialize model_performance to ensure no duplicates and accurate metrics
model_performance = []

# Re-evaluate models and collect metrics
log_reg_metrics = evaluate_model(log_reg_model, X_val_processed, y_val, 'Logistic Regression')
model_performance.append(log_reg_metrics)

rf_metrics = evaluate_model(rf_model, X_val_processed, y_val, 'Random Forest')
model_performance.append(rf_metrics)

# Get predictions and probabilities from the PyTorch model for evaluation
mlp_model.eval()
val_preds = []
val_probs = []
with torch.no_grad():
    for inputs, _ in val_loader:
        logits = mlp_model(inputs)
        probabilities = torch.sigmoid(logits)
        val_probs.extend(probabilities.cpu().numpy().flatten())
        val_preds.extend((probabilities.cpu().numpy().flatten() > 0.5).astype(int))

mlp_metrics = evaluate_pytorch_model(y_val.values, val_preds, val_probs, 'PyTorch MLP')
model_performance.append(mlp_metrics)

print("Model performance metrics re-collected and ready for comparison.")
---CELL---
# Get probabilities from the Logistic Regression model on the validation set
log_reg_val_probs = log_reg_model.predict_proba(X_val_processed)[:, 1]

# Extract amounts corresponding to the validation set
val_amounts = X_val['amount'].values

# Test a range of thresholds
thresholds = np.linspace(0, 1, 100)
log_reg_profits = []

for t in thresholds:
    profit = calculate_net_profit(y_val, log_reg_val_probs, val_amounts, t, average_recovery_rate, cost_per_recovery_attempt)
    log_reg_profits.append(profit)

# Find the optimal threshold
optimal_threshold_idx_lr = np.argmax(log_reg_profits)
optimal_threshold_lr = thresholds[optimal_threshold_idx_lr]
max_profit_lr = log_reg_profits[optimal_threshold_idx_lr]

print(f"Logistic Regression Optimal Threshold: {optimal_threshold_lr:.4f}")
print(f"Logistic Regression Maximum Net Profit at Optimal Threshold: ₹{max_profit_lr:,.2f}")

# Plotting the profit vs. threshold
plt.figure(figsize=(10, 6))
plt.plot(thresholds, log_reg_profits, label='Net Profit')
plt.axvline(x=optimal_threshold_lr, color='r', linestyle='--', label=f'Optimal Threshold ({optimal_threshold_lr:.4f})')
plt.title('Net Profit vs. Prediction Threshold (Logistic Regression)')
plt.xlabel('Prediction Threshold')
plt.ylabel('Net Profit (₹)')
plt.grid(True)
plt.legend()
plt.show()
---CELL---
# Get probabilities from the Random Forest model on the validation set
rf_val_probs = rf_model.predict_proba(X_val_processed)[:, 1]

# Extract amounts corresponding to the validation set
val_amounts = X_val['amount'].values

# Test a range of thresholds
thresholds = np.linspace(0, 1, 100)
rf_profits = []

for t in thresholds:
    profit = calculate_net_profit(y_val, rf_val_probs, val_amounts, t, average_recovery_rate, cost_per_recovery_attempt)
    rf_profits.append(profit)

# Find the optimal threshold
optimal_threshold_idx_rf = np.argmax(rf_profits)
optimal_threshold_rf = thresholds[optimal_threshold_idx_rf]
max_profit_rf = rf_profits[optimal_threshold_idx_rf]

print(f"Random Forest Optimal Threshold: {optimal_threshold_rf:.4f}")
print(f"Random Forest Maximum Net Profit at Optimal Threshold: ₹{max_profit_rf:,.2f}")

# Plotting the profit vs. threshold
plt.figure(figsize=(10, 6))
plt.plot(thresholds, rf_profits, label='Net Profit')
plt.axvline(x=optimal_threshold_rf, color='r', linestyle='--', label=f'Optimal Threshold ({optimal_threshold_rf:.4f})')
plt.title('Net Profit vs. Prediction Threshold (Random Forest)')
plt.xlabel('Prediction Threshold')
plt.ylabel('Net Profit (₹)')
plt.grid(True)
plt.legend()
plt.show()
---CELL---
# Get probabilities from the PyTorch MLP model on the validation set
mlp_model.eval()
mlp_val_probs = []
with torch.no_grad():
    for inputs, _ in val_loader:
        logits = mlp_model(inputs)
        probabilities = torch.sigmoid(logits)
        mlp_val_probs.extend(probabilities.cpu().numpy().flatten())

# Extract amounts corresponding to the validation set
val_amounts = X_val['amount'].values

# Test a range of thresholds
thresholds = np.linspace(0, 1, 100)
mlp_profits = []

for t in thresholds:
    profit = calculate_net_profit(y_val, np.array(mlp_val_probs), val_amounts, t, average_recovery_rate, cost_per_recovery_attempt)
    mlp_profits.append(profit)

# Find the optimal threshold
optimal_threshold_idx_mlp = np.argmax(mlp_profits)
optimal_threshold_mlp = thresholds[optimal_threshold_idx_mlp]
max_profit_mlp = mlp_profits[optimal_threshold_idx_mlp]

print(f"PyTorch MLP Optimal Threshold: {optimal_threshold_mlp:.4f}")
print(f"PyTorch MLP Maximum Net Profit at Optimal Threshold: ₹{max_profit_mlp:,.2f}")

# Plotting the profit vs. threshold
plt.figure(figsize=(10, 6))
plt.plot(thresholds, mlp_profits, label='Net Profit')
plt.axvline(x=optimal_threshold_mlp, color='r', linestyle='--', label=f'Optimal Threshold ({optimal_threshold_mlp:.4f})')
plt.title('Net Profit vs. Prediction Threshold (PyTorch MLP)')
plt.xlabel('Prediction Threshold')
plt.ylabel('Net Profit (₹)')
plt.grid(True)
plt.legend()
plt.show()
---CELL---
# Add business value metrics to model_performance list (temporarily for display)
# Create a separate list to avoid modifying model_performance for raw metrics
business_value_metrics = [
    {'Model': 'Logistic Regression', 'Optimal Threshold': optimal_threshold_lr, 'Max Net Profit (INR)': max_profit_lr},
    {'Model': 'Random Forest', 'Optimal Threshold': optimal_threshold_rf, 'Max Net Profit (INR)': max_profit_rf},
    {'Model': 'PyTorch MLP', 'Optimal Threshold': optimal_threshold_mlp, 'Max Net Profit (INR)': max_profit_mlp}
]

# Create a DataFrame from the collected model performance metrics
model_comparison_df = pd.DataFrame(model_performance)

# Merge with business value metrics
final_comparison_df = model_comparison_df.set_index('Model').merge(
    pd.DataFrame(business_value_metrics).set_index('Model'),
    left_index=True, right_index=True
)

print("\nFinal Model Performance and Business Value Comparison (Validation Set):")
display(final_comparison_df.drop(columns=['Confusion Matrix']).round(4))
---CELL---
import pandas as pd

# Create a DataFrame from the collected model performance metrics
model_comparison_df = pd.DataFrame(model_performance)

# Exclude the 'Confusion Matrix' column for a cleaner comparison table
model_comparison_display_df = model_comparison_df.drop(columns=['Confusion Matrix'])

print("\nModel Performance Comparison (Validation Set):")
display(model_comparison_display_df.round(4))

---CELL---
from sklearn.metrics import confusion_matrix

# Define hypothetical business parameters (Illustrative INR assumptions)
# These are illustrative and should be derived from actual business data.
average_recovery_rate = 0.80  # 80% of the amount is recovered if successful
cost_per_recovery_attempt = 50 # 50 INR cost for each recovery attempt

# Helper function to calculate net profit for a given threshold
def calculate_net_profit(y_true, y_probs, amounts, threshold, recovery_rate, cost_per_attempt):
    y_pred_threshold = (y_probs >= threshold).astype(int)
    cm = confusion_matrix(y_true, y_pred_threshold)
    tn, fp, fn, tp = cm.ravel()

    # Calculate costs and benefits
    # TP: successful recovery, benefit = amount * recovery_rate - cost_per_attempt
    # FP: failed attempt, cost = cost_per_attempt
    # FN: missed recovery, cost = amount * recovery_rate (lost opportunity)
    # TN: correct non-attempt, cost = 0

    # We need the actual amounts for TP/FP/FN/TN categories
    # To do this accurately, we need to filter `amounts` based on `y_true` and `y_pred_threshold`
    true_pos_amounts = amounts[(y_true == 1) & (y_pred_threshold == 1)]
    false_pos_amounts = amounts[(y_true == 0) & (y_pred_threshold == 1)]
    false_neg_amounts = amounts[(y_true == 1) & (y_pred_threshold == 0)]

    # Total benefits from true positives
    total_tp_benefit = (true_pos_amounts * recovery_rate).sum() - (tp * cost_per_attempt)

    # Total costs from false positives
    total_fp_cost = fp * cost_per_attempt

    # Total lost opportunity from false negatives
    total_fn_cost = (false_neg_amounts * recovery_rate).sum()

    net_profit = total_tp_benefit - total_fp_cost - total_fn_cost
    return net_profit

print("Business cost parameters and net profit calculation function defined.")
---CELL---
# Get probabilities from the Logistic Regression model on the validation set
log_reg_val_probs = log_reg_model.predict_proba(X_val_processed)[:, 1]

# Extract amounts corresponding to the validation set
val_amounts = X_val['amount'].values

# Test a range of thresholds
thresholds = np.linspace(0, 1, 100)
log_reg_profits = []

for t in thresholds:
    profit = calculate_net_profit(y_val, log_reg_val_probs, val_amounts, t, average_recovery_rate, cost_per_recovery_attempt)
    log_reg_profits.append(profit)

# Find the optimal threshold
optimal_threshold_idx_lr = np.argmax(log_reg_profits)
optimal_threshold_lr = thresholds[optimal_threshold_idx_lr]
max_profit_lr = log_reg_profits[optimal_threshold_idx_lr]

print(f"Logistic Regression Optimal Threshold: {optimal_threshold_lr:.4f}")
print(f"Logistic Regression Maximum Net Profit at Optimal Threshold: ₹{max_profit_lr:,.2f}")

# Plotting the profit vs. threshold
plt.figure(figsize=(10, 6))
plt.plot(thresholds, log_reg_profits, label='Net Profit')
plt.axvline(x=optimal_threshold_lr, color='r', linestyle='--', label=f'Optimal Threshold ({optimal_threshold_lr:.4f})')
plt.title('Net Profit vs. Prediction Threshold (Logistic Regression)')
plt.xlabel('Prediction Threshold')
plt.ylabel('Net Profit (₹)')
plt.grid(True)
plt.legend()
plt.show()
---CELL---
# Get probabilities from the Random Forest model on the validation set
rf_val_probs = rf_model.predict_proba(X_val_processed)[:, 1]

# Extract amounts corresponding to the validation set
val_amounts = X_val['amount'].values

# Test a range of thresholds
thresholds = np.linspace(0, 1, 100)
rf_profits = []

for t in thresholds:
    profit = calculate_net_profit(y_val, rf_val_probs, val_amounts, t, average_recovery_rate, cost_per_recovery_attempt)
    rf_profits.append(profit)

# Find the optimal threshold
optimal_threshold_idx_rf = np.argmax(rf_profits)
optimal_threshold_rf = thresholds[optimal_threshold_idx_rf]
max_profit_rf = rf_profits[optimal_threshold_idx_rf]

print(f"Random Forest Optimal Threshold: {optimal_threshold_rf:.4f}")
print(f"Random Forest Maximum Net Profit at Optimal Threshold: ₹{max_profit_rf:,.2f}")

# Plotting the profit vs. threshold
plt.figure(figsize=(10, 6))
plt.plot(thresholds, rf_profits, label='Net Profit')
plt.axvline(x=optimal_threshold_rf, color='r', linestyle='--', label=f'Optimal Threshold ({optimal_threshold_rf:.4f})')
plt.title('Net Profit vs. Prediction Threshold (Random Forest)')
plt.xlabel('Prediction Threshold')
plt.ylabel('Net Profit (₹)')
plt.grid(True)
plt.legend()
plt.show()
---CELL---
# Get probabilities from the PyTorch MLP model on the validation set
mlp_model.eval()
mlp_val_probs = []
with torch.no_grad():
    for inputs, _ in val_loader:
        logits = mlp_model(inputs)
        probabilities = torch.sigmoid(logits)
        mlp_val_probs.extend(probabilities.cpu().numpy().flatten())

# Extract amounts corresponding to the validation set
val_amounts = X_val['amount'].values

# Test a range of thresholds
thresholds = np.linspace(0, 1, 100)
mlp_profits = []

for t in thresholds:
    profit = calculate_net_profit(y_val, np.array(mlp_val_probs), val_amounts, t, average_recovery_rate, cost_per_recovery_attempt)
    mlp_profits.append(profit)

# Find the optimal threshold
optimal_threshold_idx_mlp = np.argmax(mlp_profits)
optimal_threshold_mlp = thresholds[optimal_threshold_idx_mlp]
max_profit_mlp = mlp_profits[optimal_threshold_idx_mlp]

print(f"PyTorch MLP Optimal Threshold: {optimal_threshold_mlp:.4f}")
print(f"PyTorch MLP Maximum Net Profit at Optimal Threshold: ₹{max_profit_mlp:,.2f}")

# Plotting the profit vs. threshold
plt.figure(figsize=(10, 6))
plt.plot(thresholds, mlp_profits, label='Net Profit')
plt.axvline(x=optimal_threshold_mlp, color='r', linestyle='--', label=f'Optimal Threshold ({optimal_threshold_mlp:.4f})')
plt.title('Net Profit vs. Prediction Threshold (PyTorch MLP)')
plt.xlabel('Prediction Threshold')
plt.ylabel('Net Profit (₹)')
plt.grid(True)
plt.legend()
plt.show()
---CELL---
import pandas as pd

# Add business value metrics to model_performance list
model_performance_business = [
    {'Model': 'Logistic Regression', 'Optimal Threshold': optimal_threshold_lr, 'Max Net Profit (INR)': max_profit_lr},
    {'Model': 'Random Forest', 'Optimal Threshold': optimal_threshold_rf, 'Max Net Profit (INR)': max_profit_rf},
    {'Model': 'PyTorch MLP', 'Optimal Threshold': optimal_threshold_mlp, 'Max Net Profit (INR)': max_profit_mlp}
]

# Create a DataFrame from the collected model performance metrics and drop duplicates based on 'Model'
model_comparison_df_clean = pd.DataFrame(model_performance).drop_duplicates(subset=['Model'])

# Merge with business value metrics
final_comparison_df = model_comparison_df_clean.set_index('Model').merge(
    pd.DataFrame(model_performance_business).set_index('Model'),
    left_index=True, right_index=True
)

print("\nFinal Model Performance and Business Value Comparison (Validation Set):")
display(final_comparison_df.drop(columns=['Confusion Matrix']).round(4))
---CELL---
# Programmatically select the best model based on 'Max Net Profit (INR)'
best_model_row = final_comparison_df.loc[final_comparison_df['Max Net Profit (INR)'].idxmax()]
final_model_name = best_model_row.name

print(f"The final model selected based on maximum net profit on the validation set is: {final_model_name}")

# Retrieve the optimal threshold for the selected model
if final_model_name == 'Logistic Regression':
    final_optimal_threshold = optimal_threshold_lr
    final_model = log_reg_model
elif final_model_name == 'Random Forest':
    final_optimal_threshold = optimal_threshold_rf
    final_model = rf_model
elif final_model_name == 'PyTorch MLP':
    final_optimal_threshold = optimal_threshold_mlp
    final_model = mlp_model
else:
    raise ValueError("Selected model name not recognized.")

print(f"Optimal threshold for {final_model_name}: {final_optimal_threshold:.4f}")
---CELL---
# Evaluate Logistic Regression on Test Set
print("\n--- Logistic Regression Test Set Evaluation ---")
log_reg_test_metrics = evaluate_model(log_reg_model, X_test_processed, y_test, 'Logistic Regression (Test)')
log_reg_test_metrics['Threshold Used'] = 0.5 # Explicitly state the default threshold

# Evaluate Random Forest on Test Set
print("\n--- Random Forest Test Set Evaluation ---")
rf_test_metrics = evaluate_model(rf_model, X_test_processed, y_test, 'Random Forest (Test)')
rf_test_metrics['Threshold Used'] = 0.5 # Explicitly state the default threshold

# Evaluate PyTorch MLP on Test Set
print("\n--- PyTorch MLP Test Set Evaluation ---")
mlp_model.eval() # Set MLP to evaluation mode
test_preds = []
test_probs = []
# Convert test data to PyTorch tensors for MLP evaluation
X_test_tensor = torch.tensor(X_test_processed, dtype=torch.float32)
y_test_tensor = torch.tensor(y_test.values, dtype=torch.float32).unsqueeze(1)
test_dataset = TensorDataset(X_test_tensor, y_test_tensor)
test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

with torch.no_grad():
    for inputs, _ in test_loader:
        logits = mlp_model(inputs)
        probabilities = torch.sigmoid(logits)
        test_probs.extend(probabilities.cpu().numpy().flatten())
        # Use final_optimal_threshold for prediction
        test_preds.extend((probabilities.cpu().numpy().flatten() >= final_optimal_threshold).astype(int))

mlp_test_metrics = evaluate_pytorch_model(y_test.values, test_preds, test_probs, 'PyTorch MLP (Test)')
mlp_test_metrics['Threshold Used'] = final_optimal_threshold # Explicitly state the optimal threshold

# Collect all test metrics for comparison
test_model_performance = [
    log_reg_test_metrics,
    rf_test_metrics,
    mlp_test_metrics
]

test_comparison_df = pd.DataFrame(test_model_performance).drop(columns=['Confusion Matrix'])
print("\nModel Performance Comparison (Test Set):")
display(test_comparison_df.round(4))
---CELL---
# Calculate batch-level revenue metrics for the final selected model on the test set

# Get probabilities for the final model on the test set
if final_model_name == 'Logistic Regression':
    final_model_test_probs = log_reg_model.predict_proba(X_test_processed)[:, 1]
elif final_model_name == 'Random Forest':
    final_model_test_probs = rf_model.predict_proba(X_test_processed)[:, 1]
elif final_model_name == 'PyTorch MLP':
    final_model.eval()
    mlp_test_probs_list = []
    with torch.no_grad():
        for inputs, _ in test_loader:
            logits = final_model(inputs)
            probabilities = torch.sigmoid(logits)
            mlp_test_probs_list.extend(probabilities.cpu().numpy().flatten())
    final_model_test_probs = np.array(mlp_test_probs_list)

# Apply the optimal threshold to get predictions
final_model_test_preds = (final_model_test_probs >= final_optimal_threshold).astype(int)

# Extract original amounts from the test set
test_amounts = X_test['amount'].values

# Confusion Matrix for detailed analysis
cm_final_test = confusion_matrix(y_test, final_model_test_preds)
tn, fp, fn, tp = cm_final_test.ravel()

# Total at-risk revenue (sum of ALL amounts in the test set, as all could be candidates for recovery)
total_at_risk_revenue = test_amounts.sum() # Changed as per user request

# Amount recovered (from True Positives)
true_pos_amounts = test_amounts[(y_test == 1) & (final_model_test_preds == 1)]
amount_recovered = (true_pos_amounts * average_recovery_rate).sum()

# Number of successful recovery decisions (True Positives)
num_successful_recovery_decisions = tp

# Number of false-positive interventions (False Positives)
num_false_positive_interventions = fp

# Total profit calculation using the function
max_profit_test = calculate_net_profit(y_test, final_model_test_probs, test_amounts, final_optimal_threshold, average_recovery_rate, cost_per_recovery_attempt)

print(f"\n--- Batch-Level Revenue Metrics for {final_model_name} on Test Set ---")
print(f"Total at-risk revenue (sum of all test transaction amounts): ₹{total_at_risk_revenue:,.2f}") # Updated description
print(f"Amount recovered (based on TP): ₹{amount_recovered:,.2f}")
print(f"Net Profit at Optimal Threshold: ₹{max_profit_test:,.2f}")
print(f"Number of successful recovery decisions (TP): {num_successful_recovery_decisions}")
print(f"Number of false-positive interventions (FP): {num_false_positive_interventions}")

# Display confusion matrix for the final model on the test set
disp = ConfusionMatrixDisplay(confusion_matrix=cm_final_test, display_labels=[False, True])
disp.plot(cmap=plt.cm.Blues)
plt.title(f'Confusion Matrix for {final_model_name} (Test Set)')
plt.show()
---CELL---
import joblib
import json
import os

# Create a directory to save artifacts
artifacts_dir = 'model_artifacts'
os.makedirs(artifacts_dir, exist_ok=True)

# Save the preprocessor
joblib.dump(preprocessor, os.path.join(artifacts_dir, 'preprocessor.joblib'))
print("Preprocessor saved.")

# Save the final model
if final_model_name == 'PyTorch MLP':
    torch.save(final_model.state_dict(), os.path.join(artifacts_dir, 'final_mlp_model.pth'))
    print("PyTorch MLP model state_dict saved.")
else:
    joblib.dump(final_model, os.path.join(artifacts_dir, f'final_{final_model_name.lower().replace(" ", "_")}_model.joblib'))
    print(f"{final_model_name} model saved.")

# Save all_processed_feature_names
with open(os.path.join(artifacts_dir, 'feature_names.json'), 'w') as f:
    json.dump(all_processed_feature_names, f)
print("Feature names saved.")

# Save metadata including the optimal threshold and business assumptions
metadata = {
    'final_model_name': final_model_name,
    'optimal_prediction_threshold': final_optimal_threshold,
    'business_assumptions': {
        'average_recovery_rate': average_recovery_rate,
        'cost_per_recovery_attempt': cost_per_recovery_attempt
    },
    'notes': 'Business recovery rate and intervention cost are illustrative assumptions based on synthetic/test-mode data.'
}

# Add MLP architecture details if the final model is MLP
if final_model_name == 'PyTorch MLP':
    mlp_architecture = {
        'input_size': input_size,
        'layers': [64, 32, 16, 1],
        'activation': 'ReLU',
        'dropout_rate': 0.3,
        'output_activation': 'Sigmoid (implicitly handled by BCEWithLogitsLoss during training, applied explicitly for prediction probabilities)'
    }
    metadata['mlp_architecture'] = mlp_architecture

with open(os.path.join(artifacts_dir, 'model_metadata.json'), 'w') as f:
    json.dump(metadata, f, indent=4)
print("Model metadata saved.")

print(f"All artifacts saved to '{artifacts_dir}' directory.")
---CELL---
import joblib
import json
import pandas as pd
import torch
import torch.nn as nn

# Define the MLP architecture (must be the same as trained)
class MLP(nn.Module):
    def __init__(self, input_size):
        super(MLP, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(input_size, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(16, 1)
        )

    def forward(self, x):
        return self.network(x)

def predict_recovery(transaction_df: pd.DataFrame):
    """
    Predicts the recovery probability and risk category for new transaction(s).

    Args:
        transaction_df (pd.DataFrame): A DataFrame containing new transaction data.
                                       Must have the same columns as the original training data
                                       (excluding 'transaction_id', 'customer_id', and 'recovered').

    Returns:
        tuple: A tuple containing:
            - pd.Series: Recovery probability for each transaction.
            - pd.Series: Risk category for each transaction ('Recovery Likely', 'High Risk of Non-Recovery').
    """
    artifacts_dir = 'model_artifacts'

    # Load preprocessor
    preprocessor_loaded = joblib.load(os.path.join(artifacts_dir, 'preprocessor.joblib'))

    # Load metadata to get final model name and optimal threshold
    with open(os.path.join(artifacts_dir, 'model_metadata.json'), 'r') as f:
        metadata_loaded = json.load(f)
    final_model_name_loaded = metadata_loaded['final_model_name']
    optimal_threshold_loaded = metadata_loaded['optimal_prediction_threshold']

    # Feature Engineering (must match training steps)
    df_pred_fe = transaction_df.copy()
    df_pred_fe['success_failure_ratio'] = df_pred_fe['previous_successes'] / (df_pred_fe['previous_failures'] + 1)
    df_pred_fe['total_previous_transactions'] = df_pred_fe['previous_successes'] + df_pred_fe['previous_failures']

    # Drop identifiers if they exist in the input (they should not be used as features)
    if 'transaction_id' in df_pred_fe.columns:
        df_pred_fe = df_pred_fe.drop(columns=['transaction_id'])
    if 'customer_id' in df_pred_fe.columns:
        df_pred_fe = df_pred_fe.drop(columns=['customer_id'])
    if 'recovered' in df_pred_fe.columns:
        df_pred_fe = df_pred_fe.drop(columns=['recovered'])

    # Preprocess the features
    X_processed_new = preprocessor_loaded.transform(df_pred_fe)

    # Load the final model
    if final_model_name_loaded == 'PyTorch MLP':
        # Need input size from the preprocessor output
        input_size_mlp = X_processed_new.shape[1]
        model_loaded = MLP(input_size_mlp)
        model_loaded.load_state_dict(torch.load(os.path.join(artifacts_dir, 'final_mlp_model.pth')))
        model_loaded.eval()
        # Convert to tensor and get predictions
        X_processed_tensor = torch.tensor(X_processed_new, dtype=torch.float32)
        with torch.no_grad():
            logits = model_loaded(X_processed_tensor)
            probabilities = torch.sigmoid(logits).cpu().numpy().flatten()
    else:
        model_loaded = joblib.load(os.path.join(artifacts_dir, f'final_{final_model_name_loaded.lower().replace(" ", "_")}_model.joblib'))
        probabilities = model_loaded.predict_proba(X_processed_new)[:, 1]

    # Determine risk category based on the optimal threshold
    risk_category = pd.Series(probabilities).apply(lambda p: 'Recovery Likely' if p >= optimal_threshold_loaded else 'High Risk of Non-Recovery')

    return pd.Series(probabilities, name='recovery_probability'), risk_category

print("predict_recovery function defined and ready for use.")
---CELL---
print("Note: The business recovery rate (80%) and cost per recovery attempt (INR 50) used in this analysis are illustrative assumptions based on synthetic/test-mode data.")

print("\n--- Dataset Size Report ---")
print(f"Total initial dataset size: {df.shape[0]} rows")
print(f"Training set size: {X_train.shape[0]} rows")
print(f"Validation set size: {X_val.shape[0]} rows")
print(f"Test set size: {X_test.shape[0]} rows")
---CELL---
# Take a sample from the original dataframe (before feature engineering for X_val)
sample_transaction = df.sample(1, random_state=100)
display(sample_transaction)

# Make a prediction using the function
prediction_probability, prediction_category = predict_recovery(sample_transaction)

print(f"\nPrediction for sample transaction:")
print(f"Recovery Probability: {prediction_probability.iloc[0]:.4f}")
print(f"Risk Category: {prediction_category.iloc[0]}")
---CELL---
# Demonstrate with multiple transactions
sample_transactions_multiple = df.sample(3, random_state=200)
display(sample_transactions_multiple)

prediction_probabilities_multiple, prediction_categories_multiple = predict_recovery(sample_transactions_multiple)

print(f"\nPredictions for multiple sample transactions:")
results_df = pd.DataFrame({
    'recovery_probability': prediction_probabilities_multiple,
    'risk_category': prediction_categories_multiple
})
display(results_df)
---CELL---
