from typing import Tuple
from urllib.parse import urlparse


def parse_s3_path(s3_path: str) -> Tuple[str, str]:
    parsed_url = urlparse(s3_path)
    if parsed_url.scheme != "s3":
        raise ValueError(f"Invalid S3 path: {s3_path}")

    bucket_name = parsed_url.netloc
    file_key = parsed_url.path.lstrip("/")
    return bucket_name, file_key
