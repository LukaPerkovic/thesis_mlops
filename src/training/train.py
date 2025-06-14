import argparse
import logging

import xgboost as xgb

from src.config.modelling import TARGET
from src.data.extraction import load_data
from src.data.preprocessing import preprocess
from src.models.model_registry import DatabricksModelRegistry
from src.models.train_model import train

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(description="Train and register a model.")
    parser.add_argument(
        "--data_path", type=str, required=True, help="Path to the training data."
    )
    parser.add_argument(
        "--model_name",
        type=str,
        required=True,
        help="Name of the model to be registered.",
    )
    parser.add_argument(
        "--performance_threshold",
        type=float,
        default=0.8,
        help="Performance threshold for production readiness.",
    )

    return parser.parse_args()


def main():
    args = parse_args()

    logging.info("Starting model training and registration.")

    logging.info(f"Loading data from {args.data_path}")
    X, y = preprocess(load_data(args.data_path), target_column=TARGET)

    logging.info("Commencing model training.")
    trained_model, score = train(
        X, y, model=xgb.XGBClassifier, performance_threshold=args.performance_threshold
    )

    if trained_model:
        logging.info("Model training completed and satisfies criteria.")
        registry = DatabricksModelRegistry()
        registry.push_model(trained_model, score, args.model_name, sample=X)
        logging.info(f"Model {args.model_name} registered successfully.")
    else:
        logging.warning("Model not ready for production.")


if __name__ == "__main__":
    main()
