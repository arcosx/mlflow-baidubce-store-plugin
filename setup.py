from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='mlflow-baidubce-store-plugin',
    version='1.0.7',
    description='A MLflow plugin that allows users to use Baidu BCE BOS as the artifact store for MLflow.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='arcosx',
    author_email='arcosx@outlook.com',
    url="https://github.com/arcosx/mlflow-baidubcestore",
    packages=find_packages(),
    install_requires=[
        'mlflow',
        'bce-python-sdk'
    ],
    entry_points={
        "mlflow.artifact_repository": [
            "bos=mlflow_baidubce_store_plugin.bce_bos_artifact_repo:BCEBOSArtifactRepository"
        ]
    },
    license="Apache License 2.0",
)