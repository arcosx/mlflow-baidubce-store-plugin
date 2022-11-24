# mlflow-baidubce-store-plugin
A **[MLflow](https://github.com/mlflow/mlflow) plugin** that allows users to use [Baidu](https://www.baidu.com/) BCE BOS([CN](https://cloud.baidu.com/doc/BOS/index.html)/[EN](https://intl.cloud.baidu.com/product/bos.html)) as the artifact store for MLflow.

## Example

```shell
pip install mlflow-baidubce-store-plugin -U
```
```python
import mlflow.pyfunc
import os

os.environ["MLFLOW_BOS_ENDPOINT"] = "bj.bcebos.com"
os.environ["MLFLOW_BOS_SECRET_ACCESS_KEY"] = "AK"
os.environ["MLFLOW_BOS_KEY_ID"] = "SK"

class Mod(mlflow.pyfunc.PythonModel):
    def predict(self, ctx, inp):
        return 8765


exp_name = "bos-exp"
mlflow.create_experiment(exp_name, artifact_location="bos://mlflow-test/")
mlflow.set_experiment(exp_name)
mlflow.pyfunc.log_model('model_test', python_model=Mod())
print(mlflow.get_artifact_uri())
mlflow.artifacts.download_artifacts(mlflow.get_artifact_uri())
```