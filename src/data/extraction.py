from io import StringIO

import boto3
import pandas as pd
from dotenv import load_dotenv

from src.utils.aws import parse_s3_path

load_dotenv()


def load_data(file_path: str) -> pd.DataFrame:
    match file_path:
        case file_path.startswith("s3://"):
            df = load_data_from_s3(parse_s3_path(*file_path))
        case _:
            df = pd.read_csv(file_path)

    return df


def load_data_from_s3(bucket_name: str, file_key: str) -> pd.DataFrame:
    s3_client = boto3.client("s3")
    response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
    data = response["Body"].read().decode("utf-8")
    return pd.read_csv(StringIO(data))
