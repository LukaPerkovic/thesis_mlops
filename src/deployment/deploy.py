import argparse
import logging

from src.models.model_registry import DatabricksModelRegistry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(description="Train and register a model.")
    parser.add_argument(
        "--endpoint_name", type=str, required=True, help="The name of the endpoint."
    )
    parser.add_argument(
        "--model_name",
        type=str,
        required=True,
        help="Name of the model to be deployed.",
    )

    return parser.parse_args()


def main():
    registry = DatabricksModelRegistry()
    args = parse_args()

    endpoint_name = args.endpoint_name
    model_name = args.model_name

    logger.info(f"Creating endpoint {endpoint_name} for model {model_name}.")
    endpoint = registry.deploy_model(endpoint_name=endpoint_name, model_name=model_name)
    logger.info(f"Endpoint {endpoint} created successfully!")


if __name__ == "__main__":
    main()
