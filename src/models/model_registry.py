import mlflow
from dotenv import load_dotenv
from mlflow.tracking import Mlfow.Client
from src.models.model_definitions import Model



class DatabricksModelRegistry:
    def __init__(self):
        load_dotenv()
        self.tracking_uri = "databricks"
        mlflow.set_tracking_uri(self.tracking_uri)
        self.client = mlflow.tracking.MlflowClient()

    def _log_model(self, model: Model, name: str):
        with mlflow.start_run() as run:
            mlflow.xgboost.log_model(model=model, name=name)
            run_id = run.info.run_id
            model_uri = f"runs:/{run_id}/{name}"
        
        return run_id, model_uri

    def _register_model(self, model_uri: str, name: str, run_id: str = None):
        """
        Register a model in the MLflow Model Registry.
        """
        try:
            return self.client.create_registered_model(name)
        except mlflow.exceptions.MlflowException as e:
            return self.client.create_model_version(
                name=name,
                source=model_uri,
                run_id=run_id
            )

    def get_model_version(self, name: str, version: int):
        """
        Get a specific version of a registered model.
        """
        return self.client.get_model_version(name, version)

    def push_model(self, model: Model, name: str):
        """
        Push a model to the MLflow Model Registry.
        """
        run_id, model_uri = self._log_model(model, name)
        return self._register_model(model_uri, name, run_id)
