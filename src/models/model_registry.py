import os

import mlflow
from dotenv import load_dotenv
from mlflow import MlflowClient
from mlflow.deployments import get_deploy_client
from pandas import DataFrame

from src.models.model_definitions import Model


class DatabricksModelRegistry:
    def __init__(self):
        load_dotenv()
        mlflow.set_tracking_uri("databricks")
        mlflow.set_registry_uri("databricks-uc")
        self.client = MlflowClient()
        self.catalog_name = "workspace"
        self.schema_name = "default"

    def _log_model(self, model: Model, score: tuple, name: str, sample: DataFrame):
        experiment_name = (
            f"/Users/{os.getenv('DBX_USER')}/fraud_detection_model_registry_experiment"
        )
        experiment = self.client.get_experiment_by_name(experiment_name)
        if experiment is None:
            experiment_id = self.client.create_experiment(experiment_name)
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
            model_version_class = mlflow.register_model(model_uri, name)
            self.client.set_registered_model_alias(
                name, "champion", int(model_version_class.version)
            )

        except mlflow.exceptions.MlflowException as mlflow_raise:
            raise mlflow_raise

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
        self._register_model(
            model_uri, f"{self.catalog_name}.{self.schema_name}.{name}", run_id
        )

    def deploy_model(self, endpoint_name: str, model_name: str):
        model_full_name = f"{self.catalog_name}.{self.schema_name}.{model_name}"
        deploy_client = get_deploy_client("databricks")
        champion_version = self.client.get_model_version_by_alias(
            model_full_name, "champion"
        )

        endpoint = deploy_client.create_endpoint(
            name=endpoint_name,
            config={
                "served_entities": [
                    {
                        "entity_name": model_full_name,
                        "entity_version": champion_version.version,
                        "workload_size": "Small",
                        "scale_to_zero_enabled": True,
                    }
                ],
                "traffic_config": {
                    "routes": [
                        {
                            "served_model_name": f"{model_name}-{champion_version.version}",
                            "traffic_percentage": 100,
                        }
                    ]
                },
            },
        )
        return endpoint


if __name__ == "__main__":
    registry = DatabricksModelRegistry()

    print(registry.client)
