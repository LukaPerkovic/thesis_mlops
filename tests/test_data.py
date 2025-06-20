from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from src.data import extraction


@patch("src.data.extraction.parse_s3_path")
@patch("src.data.extraction.load_data_from_s3")
def test_load_data_s3(mock_load_data_from_s3, mock_parse_s3_path):
    mock_parse_s3_path.return_value = ("bucket", "key")
    mock_df = pd.DataFrame({"a": [1, 2]})
    mock_load_data_from_s3.return_value = mock_df
    result = extraction.load_data("s3://bucket/key")
    assert result.equals(mock_df)
    mock_parse_s3_path.assert_called_once()
    mock_load_data_from_s3.assert_called_once_with("bucket", "key")


@patch("src.data.extraction.parse_s3_path")
@patch("src.data.extraction.save_data_to_s3")
def test_save_data_s3(mock_save_data_to_s3, mock_parse_s3_path):
    mock_parse_s3_path.return_value = ("bucket", "key")
    df = pd.DataFrame({"a": [1, 2]})
    extraction.save_data(df, "s3://bucket/key")
    mock_parse_s3_path.assert_called_once()
    mock_save_data_to_s3.assert_called_once_with(df, "bucket", "key")


@patch("src.data.extraction.find_most_recent_file_in_s3")
@patch("src.data.extraction.boto3.client")
@patch("pandas.read_csv")
def test_load_data_from_s3(mock_read_csv, mock_boto_client, mock_find_most_recent):
    mock_s3 = MagicMock()
    mock_boto_client.return_value = mock_s3
    mock_find_most_recent.return_value = "file.csv"
    mock_s3.get_object.return_value = {
        "Body": MagicMock(read=MagicMock(return_value=b"a,b\n1,2\n"))
    }
    mock_df = pd.DataFrame({"a": [1], "b": [2]})
    mock_read_csv.return_value = mock_df
    result = extraction.load_data_from_s3("bucket", "prefix")
    assert result.equals(mock_df)
    mock_find_most_recent.assert_called_once_with(mock_s3, "bucket", "prefix")
    mock_s3.get_object.assert_called_once_with(Bucket="bucket", Key="file.csv")
    mock_read_csv.assert_called_once()


@patch("src.data.extraction.boto3.client")
def test_save_data_to_s3_success(mock_boto_client):
    mock_s3 = MagicMock()
    mock_boto_client.return_value = mock_s3
    df = pd.DataFrame({"a": [1, 2]})
    # Should not raise
    extraction.save_data_to_s3(df, "bucket", "key")
    mock_s3.put_object.assert_called_once()
    args, kwargs = mock_s3.put_object.call_args
    assert kwargs["Bucket"] == "bucket"
    assert kwargs["Key"] == "key"
    assert isinstance(kwargs["Body"], str)


@patch("src.data.extraction.boto3.client")
def test_save_data_to_s3_exception(mock_boto_client):
    mock_s3 = MagicMock()
    mock_boto_client.return_value = mock_s3
    mock_s3.put_object.side_effect = Exception("fail")
    df = pd.DataFrame({"a": [1, 2]})
    with pytest.raises(Exception):
        extraction.save_data_to_s3(df, "bucket", "key")


def test_find_most_recent_file_in_s3_no_csv():
    mock_s3 = MagicMock()
    mock_s3.list_objects_v2.return_value = {
        "Contents": [{"Key": "a.txt", "LastModified": 1}]
    }
    with pytest.raises(ValueError):
        extraction.find_most_recent_file_in_s3(mock_s3, "bucket", "prefix")
