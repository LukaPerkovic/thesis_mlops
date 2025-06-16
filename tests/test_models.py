from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

from src.models.model_definitions import ModelEvaluation, ModelOptimization
from src.models.model_registry import DatabricksModelRegistry


class DummyModel:
    def __init__(self, **kwargs):
        pass

    def fit(self, X, y):
        self.mean = y.mean()

    def predict(self, X):
        # Predict 1 if mean > 0.5 else 0
        return np.ones(len(X)) if self.mean > 0.5 else np.zeros(len(X))


@pytest.fixture
def sample_data():
    X = pd.DataFrame({"a": [1, 2, 3, 4, 5]})
    y = pd.Series([0, 1, 0, 1, 1])
    return X, y


def test_model_evaluation_evaluate_model(sample_data):
    X, y = sample_data
    model = DummyModel()
    evaluator = ModelEvaluation(X, y)
    score = evaluator.evaluate_model(model)
    assert 0.0 <= score <= 1.0


@patch("src.models.model_definitions.optuna.create_study")
def test_model_optimization_optimize_returns_none_if_below_threshold(
    mock_create_study, sample_data
):
    mock_study = MagicMock()
    mock_study.best_params = {}
    mock_study.best_value = 0.0
    mock_create_study.return_value = mock_study
    mock_study.optimize = lambda func, n_trials: None

    X, y = sample_data
    opt = ModelOptimization(X, y, DummyModel, threshold=1.0)
    model = opt.optimize(n_trials=1)
    assert model is None
    assert opt.production_ready is False


def test_model_optimization_get_score(sample_data):
    X, y = sample_data
    opt = ModelOptimization(X, y, DummyModel, threshold=0.0)
    # Set score manually for test
    opt.score = ("f1_score", 0.5)
    assert opt.get_score() == ("f1_score", 0.5)


@patch("src.models.model_registry.mlflow")
@patch("src.models.model_registry.MlflowClient")
def test_databricks_model_registry_log_and_register(mock_mlflow_client, mock_mlflow):
    # Setup
    registry = DatabricksModelRegistry()
    model = DummyModel()
    score = ("f1_score", 1.0)
    name = "test_model"
    sample = pd.DataFrame({"a": [1]})

    # Mock experiment
    mock_client = MagicMock()
    registry.client = mock_client
    mock_client.get_experiment_by_name.return_value = None
    mock_client.create_experiment.return_value = "exp_id"
    mock_run = MagicMock()
    mock_mlflow.start_run.return_value.__enter__.return_value = mock_run
    mock_run.info.run_id = "run_id"

    # Test _log_model
    run_id, model_uri = registry._log_model(model, score, name, sample)
    assert run_id == "run_id"
    assert model_uri.endswith(name)

    # Test _register_model
    mock_mlflow.register_model.return_value.version = 1
    registry._register_model("uri", name, run_id)
    mock_client.set_registered_model_alias.assert_called_with(name, "champion", 1)


@patch("src.models.model_registry.mlflow")
@patch("src.models.model_registry.MlflowClient")
@patch("src.models.model_registry.get_deploy_client")
def test_databricks_model_registry_deploy_model(
    mock_get_deploy_client, mock_mlflow_client, mock_mlflow
):
    registry = DatabricksModelRegistry()
    mock_client = MagicMock()
    registry.client = mock_client
    mock_deploy_client = MagicMock()
    mock_get_deploy_client.return_value = mock_deploy_client
    mock_client.get_model_version_by_alias.return_value.version = 1
    mock_deploy_client.create_endpoint.return_value = {"endpoint": "ok"}

    endpoint = registry.deploy_model("endpoint_name", "model_name")
    assert endpoint == {"endpoint": "ok"}
