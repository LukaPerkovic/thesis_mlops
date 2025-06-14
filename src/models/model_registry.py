import mlflow
import os
from dotenv import load_dotenv
from mlflow import MlflowClient
from pandas import DataFrame
from src.models.model_definitions import Model


class DatabricksModelRegistry:
    def __init__(self):
        load_dotenv()
        mlflow.set_tracking_uri("databricks")
        mlflow.set_registry_uri("databricks-uc")
        self.client = MlflowClient()
        self.experiment_name = (
            f"/Users/{os.getenv('DBX_USER')}/fraud_detection_model_registry_experiment"
        )
        self.catalog_name = "workspace"
        self.schema_name = "default"

    def _log_model(self, model: Model, score: tuple, name: str, sample: DataFrame):
        experiment = self.client.get_experiment_by_name(self.experiment_name)
        if experiment is None:
            experiment_id = self.client.create_experiment(self.experiment_name)
        else:
            experiment_id = experiment.experiment_id

        with mlflow.start_run(experiment_id=experiment_id) as run:
            mlflow.xgboost.log_model(
                xgb_model=model, name=name, input_example=sample.iloc[[0]]
            )
            mlflow.log_metric(score[0], score[1])
            run_id = run.info.run_id
            model_uri = f"runs:/{run_id}/{name}"

            return run_id, model_uri

    def _register_model(self, model_uri: str, name: str, run_id: str = None):
        """
        Register a model in the MLflow Model Registry.
        """
        try:
            return self.client.create_registered_model(name)
        except mlflow.exceptions.MlflowException:
            return self.client.create_model_version(
                name=name, source=model_uri, run_id=run_id
            )

    def get_model_version(self, name: str, version: int):
        """
        Get a specific version of a registered model.
        """
        return self.client.get_model_version(name, version)

    def push_model(self, model: Model, score: tuple, name: str, sample: DataFrame):
        """
        Push a model to the MLflow Model Registry.
        """
        run_id, model_uri = self._log_model(model, score, name, sample)
        return self._register_model(
            model_uri, f"{self.catalog_name}.{self.schema_name}.{name}", run_id
        )


if __name__ == "__main__":
    registry = DatabricksModelRegistry()

    print(registry.client)
