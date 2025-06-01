import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import joblib # For saving the model and scaler

# --- Configuration ---
CSV_FILENAME = 'robot_arm_training_data.csv'
MODEL_FILENAME = 'robot_arm_model.pkl'
SCALER_FILENAME = 'input_scaler.pkl'
NUM_SERVOS = 6

def train_model():
    # 1. Load Data
    try:
        df = pd.read_csv(CSV_FILENAME)
    except FileNotFoundError:
        print(f"Error: Training data file '{CSV_FILENAME}' not found.")
        print("Please run the data_collector.py script first to generate data.")
        return

    if df.empty:
        print(f"Error: Training data file '{CSV_FILENAME}' is empty.")
        return
    
    print(f"Loaded {len(df)} data points from '{CSV_FILENAME}'.")

    # 2. Define Features (X) and Target (y)
    # Input features: current angles of 6 servos + distance
    feature_cols = [f's{i+1}_curr' for i in range(NUM_SERVOS)] + ['distance']
    # Target outputs: target angles for 6 servos
    target_cols = [f's{i+1}_target' for i in range(NUM_SERVOS)]

    X = df[feature_cols]
    y = df[target_cols]

    # 3. Preprocessing: Scale input features
    # Scaling helps models (especially neural networks, but also beneficial for others)
    # to converge faster and perform better.
    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)
    print("Input features scaled using MinMaxScaler.")

    # 4. Split Data into Training and Testing sets
    # test_size=0.2 means 20% of data is for testing, 80% for training
    # random_state ensures the split is the same every time you run (for reproducibility)
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
    print(f"Data split: {len(X_train)} training samples, {len(X_test)} testing samples.")

    # 5. Choose and Train Model
    # RandomForestRegressor is a good starting point.
    # n_estimators: number of trees in the forest. More trees can improve performance but increase training time.
    # random_state: for reproducibility of model training.
    # n_jobs=-1: use all available CPU cores for training (can speed it up).
    print("Training RandomForestRegressor model...")
    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1, max_depth=20, min_samples_split=5, min_samples_leaf=2)
    # You can experiment with hyperparameters like n_estimators, max_depth, min_samples_split, min_samples_leaf
    
    model.fit(X_train, y_train)
    print("Model training complete.")

    # 6. Evaluate the Model on the Test Set
    predictions = model.predict(X_test)

    mse = mean_squared_error(y_test, predictions)
    r2 = r2_score(y_test, predictions) # R-squared: 1 is perfect, 0 means model does no better than predicting the mean

    print("\n--- Model Evaluation ---")
    print(f"Mean Squared Error (MSE) on Test Set: {mse:.4f}")
    # MSE is per output. If you have 6 outputs, this is an average or array.
    # For multi-output, scikit-learn's mean_squared_error by default averages the MSEs of each output.
    print(f"R-squared (R2) Score on Test Set: {r2:.4f}")

    # You can also print MSE for each individual servo output if desired:
    for i in range(NUM_SERVOS):
        servo_mse = mean_squared_error(y_test.iloc[:, i], predictions[:, i])
        print(f"  MSE for Servo {i+1} target: {servo_mse:.4f}")
    
    if r2 < 0.5: # Arbitrary threshold, adjust based on your needs
        print("\nWARNING: R2 score is low. The model might not be performing well.")
        print("Consider: collecting more/better data, trying different model hyperparameters, or a different model type.")

    # 7. Save the Trained Model and the Scaler
    joblib.dump(model, MODEL_FILENAME)
    print(f"\nTrained model saved to '{MODEL_FILENAME}'")
    joblib.dump(scaler, SCALER_FILENAME)
    print(f"Input scaler saved to '{SCALER_FILENAME}'")
    print("\n--- Training Finished ---")

if __name__ == "__main__":
    train_model()