from typing import Protocol

import optuna
import pandas as pd
from sklearn.metrics import f1_score
from sklearn.model_selection import train_test_split


class Model(Protocol):
    def fit(self, X, y): ...

    def predict(self, X): ...


class ModelEvaluation:
    """
    Trains and evalutes the model.
    """

    def __init__(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        test_size: float = 0.2,
        random_state: int = 42,
    ):
        """
        param X: features
        param y: target
        param test_size: size of the test set
        param random_state: random state for reproducibility
        """
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )

    def evaluate_model(self, model: Model) -> float:
        model.fit(self.X_train, self.y_train)
        y_pred = model.predict(self.X_test)
        f1 = f1_score(self.y_test, y_pred)
        return f1


class ModelOptimization(ModelEvaluation):
    """
    Optimizes the model by tuning hyperparameters.
    """

    def __init__(self, X: pd.DataFrame, y: pd.Series, model: Model, threshold: float):
        super().__init__(X, y)
        """
    param params: dictionary of hyperparameters
    param model: model to be optimized
    param threshold: threshold to check if performance is good enough
    """
        self.X: pd.DataFrame = X
        self.y: pd.Series = y
        self.model: Model = model
        self.score: tuple = ("f1_score", 0.0)
        self.threshold: float = threshold
        self.production_ready: bool = False

    def _set_objective(self, trial):
        param = {
            "max_depth": trial.suggest_int("max_depth", 3, 10),
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3),
            "n_estimators": trial.suggest_int("n_estimators", 100, 1000),
            "subsample": trial.suggest_float("subsample", 0.5, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 1.0),
            "objective": "binary:logistic",
        }
        model = self.model(**param)

        return self.evaluate_model(model)

    def _check_performance(self, candidate_model: Model) -> bool:
        y_pred = candidate_model.predict(self.X_test)
        f1 = f1_score(self.y_test, y_pred)
        return f1 > self.threshold

    def optimize(self, n_trials: int = 20) -> Model:
        """
        Optimizes the model by tuning hyperparameters. If the score is high enough
        the model is deemed ready for production.

        param n_trials: number of trials to run
        """
        study = optuna.create_study(direction="maximize")
        study.optimize(self._set_objective, n_trials=n_trials)
        best_params = study.best_params
        best_model = self.model(**best_params)
        best_model.fit(self.X_train, self.y_train)

        if self._check_performance(best_model):
            final_model = self.model(**best_params)
            final_model.fit(self.X, self.y)
            self.production_ready = True
            self.score = ("f1_score", study.best_value)
        else:
            self.production_ready = False
            final_model = None

        return final_model

    def get_score(self) -> tuple:
        """
        Returns the final score of the model if it satisfies the criteria.
        """
        return self.score
