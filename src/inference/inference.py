import argparse
import json
import logging
import os
from typing import Any, Dict, Union

import pandas as pd
import requests
from dotenv import load_dotenv

from src.data.extraction import load_data, save_data

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(description="Train and register a model.")
    parser.add_argument(
        "--input_data_path", type=str, required=True, help="Path to the inference data."
    )

    parser.add_argument(
        "--output_data_path",
        type=str,
        required=True,
        help="Path to export inference data.",
    )

    return parser.parse_args()


def create_serving_json(data: Union[Dict[str, Any], pd.DataFrame]) -> Dict[str, Any]:
    return {
        "inputs": {name: data[name].tolist() for name in data.keys()}
        if isinstance(data, dict)
        else data.to_list()
    }


def prepare_dataset(dataset: Union[pd.DataFrame, Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "dataframe_split": dataset.to_dict(orient="split")
        if isinstance(dataset, pd.DataFrame)
        else create_serving_json(dataset)
    }


def send_request(data_json: str) -> Dict[str, Any]:
    url = os.getenv("ENDPOINT_URL")
    headers = {
        "Authorization": f"Bearer {os.getenv('DATABRICKS_TOKEN')}",
        "Content-Type": "application/json",
    }

    response = requests.post(url, headers=headers, data=data_json)
    if response.status_code != 200:
        logger.error(
            f"Request failed with status code {response.status_code}: {response.text}"
        )
        response.raise_for_status()

    return response.json()


def score_model(dataset: Union[pd.DataFrame, Dict[str, Any]]) -> Dict[str, Any]:
    try:
        ds_dict = prepare_dataset(dataset)
        data_json = json.dumps(ds_dict, allow_nan=True)
        return send_request(data_json)
    except requests.RequestException as e:
        logger.error(f"Error during model scoring: {e}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON response: {e}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise


def main():
    args = parse_args()
    data = load_data(args.input_data_path)

    predictions = pd.DataFrame(score_model(data)["predictions"])
    predictions_df = pd.concat([data["id"], predictions], axis=1)
    logger.info("Results generated successfully.")

    save_data(predictions_df, args.output_data_path)
    logger.info("Results exported!")


if __name__ == "__main__":
    main()
