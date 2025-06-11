import argparse
import logging

from src.data.data_loader import load_data
from src.models.model_registry import DatabricksModelRegistry
from src.models.train_model import train

logging.basicConfig(level=loggging.INFO)
logger - logging.getLogger(__name__)

def parse_args():
    parser = argparse.ArgumentParser(description="Train and register a model.")
    parser.add_argument("--data_path", type=str, required=True, help="Path to the training data.")
    parser.add_argument("--model_name", type=str, required=True, help="Name of the model to be registered.")
    parser.add_argument("--performance_threshold", type=float, default=0.8, help="Performance threshold for production readiness.")
    
    return parser.parse_args()
    
def main():

    args = parse_args()

    X, y = load_data(args.data_path)

    trained_model = train(X, y, model_name=args.model_name, performance_threshold=args.performance_threshold)

    if trained_model:
        registry = DatabricksModelRegistry()
        registry.push_model(trained_model, args.model_name)
        logging.info(f"Model {args.model_name} registered successfully.")
    else:
        logging.warning("Model not ready for production.")

if __name__ == "__main__":
    main()