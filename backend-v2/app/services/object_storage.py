from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from app.core.config import settings


@dataclass(frozen=True)
class StoredObject:
    backend: str
    object_key: str
    size: int


class ObjectStorageService:
    """
    Store uploaded documents in S3-compatible storage when available.
    Falls back to local filesystem for development continuity.
    """

    def put_bytes(
        self,
        *,
        project_id: str,
        file_name: str,
        file_bytes: bytes,
    ) -> StoredObject:
        object_key = f"projects/{project_id}/{uuid4().hex[:12]}-{file_name}"
        if self._minio_available():
            try:
                return self._put_minio(object_key=object_key, file_bytes=file_bytes)
            except Exception:
                pass
        return self._put_local(object_key=object_key, file_bytes=file_bytes)

    def read_bytes(self, object_key: str) -> bytes:
        if object_key.startswith("local://"):
            path = Path(object_key.removeprefix("local://"))
            return path.read_bytes()
        if object_key.startswith("minio://"):
            return self._read_minio(object_key)
        raise FileNotFoundError(f"Unknown object key: {object_key}")

    def _minio_available(self) -> bool:
        return bool(settings.minio_endpoint and settings.minio_bucket)

    def _put_minio(self, *, object_key: str, file_bytes: bytes) -> StoredObject:
        from io import BytesIO

        from minio import Minio

        secure = str(settings.minio_endpoint).startswith("https://")
        endpoint = str(settings.minio_endpoint).removeprefix("http://").removeprefix("https://")
        client = Minio(
            endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=secure,
        )
        bucket = settings.minio_bucket
        if not client.bucket_exists(bucket):
            client.make_bucket(bucket)
        client.put_object(
            bucket,
            object_key,
            BytesIO(file_bytes),
            length=len(file_bytes),
        )
        return StoredObject(
            backend="minio",
            object_key=f"minio://{bucket}/{object_key}",
            size=len(file_bytes),
        )

    def _read_minio(self, object_key: str) -> bytes:
        from minio import Minio

        secure = str(settings.minio_endpoint).startswith("https://")
        endpoint = str(settings.minio_endpoint).removeprefix("http://").removeprefix("https://")
        client = Minio(
            endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=secure,
        )
        path = object_key.removeprefix("minio://")
        bucket, key = path.split("/", 1)
        response = client.get_object(bucket, key)
        try:
            return response.read()
        finally:
            response.close()
            response.release_conn()

    def _put_local(self, *, object_key: str, file_bytes: bytes) -> StoredObject:
        storage_root = Path(__file__).resolve().parents[2] / "storage"
        path = storage_root / object_key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(file_bytes)
        return StoredObject(
            backend="local",
            object_key=f"local://{path}",
            size=len(file_bytes),
        )


object_storage_service = ObjectStorageService()
