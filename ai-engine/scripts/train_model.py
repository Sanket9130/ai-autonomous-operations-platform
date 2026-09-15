"""
CLI execution script for HVAC model training and model comparison.
"""

from pathlib import Path
import sys
import pandas as pd

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.models.train import train_and_compare_models


def main():
    data_path = Path(__file__).resolve().parent.parent / "data" / "raw" / "hvac_sensor_data.csv"
    if not data_path.exists():
        print(f"Error: Dataset not found at {data_path}. Run generate_sample_data.py first.")
        sys.exit(1)

    print(f"Loading telemetry dataset from {data_path}...")
    df = pd.read_csv(data_path)
    print(f"Loaded {len(df)} records. Training and evaluating models...")

    best_model, metadata = train_and_compare_models(df)

    print("\n" + "=" * 50)
    print("MODEL COMPARISON RESULTS")
    print("=" * 50)
    for model_name, metrics in metadata["comparison"].items():
        print(f"\nModel: {model_name}")
        print(f"  Recall  : {metrics['recall']:.4f}")
        print(f"  F1-Score: {metrics['f1']:.4f}")
        print(f"  ROC-AUC : {metrics['roc_auc']:.4f}")
        print(f"  Accuracy: {metrics['accuracy']:.4f}")

    print("\n" + "-" * 50)
    print(f"SELECTED BEST MODEL: {metadata['selected_model']}")
    print(f"Model saved to models/best_hvac_model.joblib")
    print(f"Metadata saved to models/model_metadata.json")
    print("=" * 50)


if __name__ == "__main__":
    main()
