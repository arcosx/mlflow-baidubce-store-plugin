import os

import posixpath
from six.moves import urllib

from mlflow.entities import FileInfo
from mlflow.exceptions import MlflowException
from mlflow.store.artifact.artifact_repo import ArtifactRepository
from mlflow.utils.file_utils import relative_path_to_artifact_path


class BCEBOSArtifactRepository(ArtifactRepository):
    """Stores artifacts on Baidu BCE BOS."""

    def __init__(self, artifact_uri, bos_client=None):
        super(BCEBOSArtifactRepository, self).__init__(artifact_uri)

        if bos_client is not None:
            self._bos_client = bos_client
            return

        from baidubce.bce_client_configuration import BceClientConfiguration
        from baidubce.auth.bce_credentials import BceCredentials
        from baidubce.services.bos.bos_client import BosClient

        bos_endpoint = os.environ.get('MLFLOW_BOS_ENDPOINT')
        bos_secret_access_key = os.environ.get('MLFLOW_BOS_SECRET_ACCESS_KEY')
        bos_access_key_id = os.environ.get('MLFLOW_BOS_KEY_ID')
        assert bos_endpoint, 'please set MLFLOW_BOS_ENDPOINT'
        assert bos_secret_access_key, 'please set MLFLOW_BOS_SECRET_ACCESS_KEY'
        assert bos_access_key_id, 'please set MLFLOW_BOS_KEY_ID'

        self._bos_config = BceClientConfiguration(credentials=BceCredentials(bos_access_key_id, bos_secret_access_key),
                                                  endpoint=bos_endpoint)
        self._bos_client = BosClient(self._bos_config)

        self.is_plugin = True

    @property
    def bos_client(self):
        return self._bos_client

    @staticmethod
    def parse_bos_uri(uri):
        """Parse an BOS URI, returning (bucket, path)"""
        parsed = urllib.parse.urlparse(uri)
        if parsed.scheme != "bos":
            raise Exception("Not an BOS URI: %s" % uri)
        path = parsed.path
        if path.startswith('/'):
            path = path[1:]
        return parsed.netloc, path

    def log_artifact(self, local_file, artifact_path=None):
        (bucket, dest_path) = self.parse_bos_uri(self.artifact_uri)
        if artifact_path:
            dest_path = posixpath.join(dest_path, artifact_path)
        dest_path = posixpath.join(
            dest_path, os.path.basename(local_file))
        self.bos_client.put_object_from_file(bucket, dest_path, local_file)

    def log_artifacts(self, local_dir, artifact_path=None):
        (bucket, dest_path) = self.parse_bos_uri(self.artifact_uri)
        if artifact_path:
            dest_path = posixpath.join(dest_path, artifact_path)
        local_dir = os.path.abspath(local_dir)
        for (root, _, filenames) in os.walk(local_dir):
            upload_path = dest_path
            if root != local_dir:
                rel_path = os.path.relpath(root, local_dir)
                rel_path = relative_path_to_artifact_path(rel_path)
                upload_path = posixpath.join(dest_path, rel_path)
            for f in filenames:
                remote_file_path = posixpath.join(upload_path, f)
                local_file_path = os.path.join(root, f)
                self.bos_client.put_object_from_file(bucket, remote_file_path, local_file_path)

    def list_artifacts(self, path=None):
        (bucket, artifact_path) = self.parse_bos_uri(self.artifact_uri)
        dest_path = artifact_path
        if path:
            dest_path = posixpath.join(dest_path, path)
        infos = []
        prefix = dest_path + "/" if dest_path else ""

        response = self.bos_client.list_objects(bucket_name=bucket, prefix=prefix, delimiter='/')

        for obj in response.contents:
            file_path = obj.key
            file_rel_path = posixpath.relpath(path=file_path, start=artifact_path)
            file_size = obj.size
            infos.append(FileInfo(file_rel_path, False, file_size))

        for subdir_path in response.common_prefixes:
            subdir_rel_path = posixpath.relpath(path=subdir_path.prefix, start=artifact_path)
            infos.append(FileInfo(subdir_rel_path, True, None))

        return sorted(infos, key=lambda f: f.path)

    def _download_file(self, remote_file_path, local_path):
        (bucket, bos_root_path) = self.parse_bos_uri(self.artifact_uri)
        bos_full_path = posixpath.join(bos_root_path, remote_file_path)
        self.bos_client.get_object_to_file(bucket, bos_full_path, local_path)

    def delete_artifacts(self, artifact_path=None):
        raise MlflowException('Not implemented yet')
