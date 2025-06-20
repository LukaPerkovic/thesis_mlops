from typing import Tuple, Union

import pandas as pd

from src.models.model_definitions import Model, ModelOptimization


def train(
    X: pd.DataFrame, y: pd.Series, model: Model, performance_threshold: float
) -> Tuple[Union[Model, None], tuple]:
    """
    Trains and optimizes the model. If the performance is below the threshold
    the model is deemed not ready for production and therefore not returned.

    param data: data to be used for training
    param model: model to be trained
    param performance_threshold: threshold to check if performance is good enough
    return: trained model and best score, or None and 0.0 if not ready for production
    """

    mo = ModelOptimization(X, y, model, performance_threshold)

    return mo.optimize(), mo.score
