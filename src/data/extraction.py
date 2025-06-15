from io import StringIO

import boto3
import pandas as pd
from dotenv import load_dotenv

from src.utils.aws import parse_s3_path

load_dotenv()


def load_data(file_path: str) -> pd.DataFrame:
    if file_path.startswith("s3://"):
        df = load_data_from_s3(parse_s3_path(*file_path))
    else:
        df = pd.read_csv(file_path)

    return df


def save_data(data: pd.DataFrame, file_path: str) -> None:
    if file_path.startswith("s3://"):
        save_data_to_s3(data, parse_s3_path(*file_path))
    else:
        data.to_csv(file_path)


def load_data_from_s3(bucket_name: str, file_key: str) -> pd.DataFrame:
    s3_client = boto3.client("s3")
    response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
    data = response["Body"].read().decode("utf-8")
    return pd.read_csv(StringIO(data))


def save_data_to_s3(df: pd.DataFrame, bucket_name: str, file_key: str) -> None:
    try:
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)
        s3_client = boto3.client("s3")
        s3_client.put_object(
            Bucket=bucket_name, Key=file_key, Body=csv_buffer.getvalue()
        )
        print(f"Data saved to {bucket_name}/{file_key}")
    except Exception as e:
        print(f"Error saving data to S3: {e}")
        raise e
