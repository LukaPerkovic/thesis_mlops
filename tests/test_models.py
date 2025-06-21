from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

from src.models.model_definitions import ModelEvaluation, ModelOptimization


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
