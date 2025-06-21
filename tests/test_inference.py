from unittest import mock
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from src.inference.inference import create_serving_json, prepare_dataset, score_model


def test_create_serving_json_with_dict():
    data = {"a": pd.Series([1, 2]), "b": pd.Series([3, 4])}
    result = create_serving_json(data)
    assert "inputs" in result
    assert set(result["inputs"].keys()) == {"a", "b"}


def test_prepare_dataset_with_dataframe():
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    result = prepare_dataset(df)
    assert "dataframe_split" in result
    assert "data" in result["dataframe_split"]


def test_prepare_dataset_with_dict():
    data = {"a": pd.Series([1, 2]), "b": pd.Series([3, 4])}
    result = prepare_dataset(data)
    assert "dataframe_split" in result
    assert "inputs" in result["dataframe_split"]


@patch("src.inference.inference.requests.post")
@patch("src.inference.inference.os.getenv")
def test_send_request_success(mock_getenv, mock_post):
    mock_getenv.side_effect = lambda k: "test_url" if k == "ENDPOINT_URL" else "token"
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"predictions": [1, 0]}
    mock_post.return_value = mock_response

    from src.inference.inference import send_request

    url = "https://test_url"
    result = send_request(url, '{"foo": "bar"}')
    assert result == {"predictions": [1, 0]}


@patch("src.inference.inference.requests.post")
@patch("src.inference.inference.os.getenv")
def test_send_request_failure(mock_getenv, mock_post):
    mock_getenv.side_effect = lambda k: "test_url" if k == "ENDPOINT_URL" else "token"
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.text = "Bad Request"
    mock_response.raise_for_status.side_effect = Exception("HTTP error")
    mock_post.return_value = mock_response

    from src.inference.inference import send_request

    with pytest.raises(Exception):
        send_request('{"foo": "bar"}')


@patch("src.inference.inference.send_request")
def test_score_model_success(mock_send_request):
    mock_send_request.return_value = {"predictions": [1, 0]}
    df = pd.DataFrame({"a": [1, 2]})
    url = "http://test-url"
    result = score_model(url, df)
    assert result == {"predictions": [1, 0]}


@patch("src.inference.inference.send_request")
def test_score_model_request_exception(mock_send_request):
    mock_send_request.side_effect = Exception("Request failed")
    df = pd.DataFrame({"a": [1, 2]})
    with pytest.raises(Exception):
        score_model(df)


@patch("src.inference.inference.save_data")
@patch("src.inference.inference.score_model")
@patch("src.inference.inference.load_data")
@patch("src.inference.inference.parse_args")
def test_main_success(
    mock_parse_args, mock_load_data, mock_score_model, mock_save_data
):
    mock_parse_args.return_value = mock.Mock(
        input_data_path="input.csv", output_data_path="output.csv"
    )
    mock_load_data.return_value = pd.DataFrame({"id": [1, 2], "a": [3, 4]})
    mock_score_model.return_value = {"predictions": [[0], [1]]}
