# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Storage utilities for on-premise deployment.

Supports local filesystem and MinIO (S3-compatible) storage backends.
"""

import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)


def ensure_storage_initialized() -> str:
    """Initialize storage backend based on configuration.

    Returns:
        str: Storage path or URI to use for artifact service
    """
    storage_type = os.getenv("STORAGE_TYPE", "local")

    if storage_type == "local":
        return _ensure_local_storage()
    elif storage_type in ["minio", "s3"]:
        return _ensure_minio_storage()
    else:
        logger.warning(f"Unknown storage type: {storage_type}, falling back to local")
        return _ensure_local_storage()


def _ensure_local_storage() -> str:
    """Initialize local filesystem storage.

    Returns:
        str: Path to local storage directory
    """
    storage_path = os.getenv("LOCAL_STORAGE_PATH", "./data/storage")
    path = Path(storage_path)

    # Create directory structure
    path.mkdir(parents=True, exist_ok=True)
    (path / "artifacts").mkdir(exist_ok=True)
    (path / "logs").mkdir(exist_ok=True)

    logger.info(f"Local storage initialized at: {path.absolute()}")
    return str(path.absolute())


def _ensure_minio_storage() -> str:
    """Initialize MinIO (S3-compatible) storage.

    Returns:
        str: MinIO bucket URI
    """
    try:
        from minio import Minio
    except ImportError:
        logger.error(
            "MinIO package not installed. Install with: pip install minio"
        )
        logger.info("Falling back to local storage")
        return _ensure_local_storage()

    endpoint_url = os.getenv("STORAGE_ENDPOINT_URL", "localhost:9000")
    # Remove http:// or https:// prefix if present
    endpoint = endpoint_url.replace("http://", "").replace("https://", "")

    access_key = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    secret_key = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    secure = os.getenv("MINIO_SECURE", "false").lower() == "true"

    try:
        client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,
        )

        # Create buckets if they don't exist
        buckets = [
            "{{cookiecutter.project_name}}-artifacts",
            "{{cookiecutter.project_name}}-logs",
        ]

        for bucket_name in buckets:
            if not client.bucket_exists(bucket_name):
                client.make_bucket(bucket_name)
                logger.info(f"Created MinIO bucket: {bucket_name}")
            else:
                logger.info(f"MinIO bucket already exists: {bucket_name}")

        # Return S3-compatible URI for artifact service
        bucket_uri = f"s3://{buckets[0]}"
        logger.info(f"MinIO storage initialized: {bucket_uri}")
        return bucket_uri

    except Exception as e:
        logger.error(f"Failed to initialize MinIO storage: {e}")
        logger.info("Falling back to local storage")
        return _ensure_local_storage()


def create_bucket_if_not_exists(bucket_name: str, project: str = None, location: str = None) -> None:
    """Create storage bucket/directory if it doesn't exist.

    This function maintains compatibility with the GCS version but works with
    local storage or MinIO based on STORAGE_TYPE environment variable.

    Args:
        bucket_name: Name of the bucket/directory to create
        project: Ignored for on-premise (kept for compatibility)
        location: Ignored for on-premise (kept for compatibility)
    """
    storage_type = os.getenv("STORAGE_TYPE", "local")

    if storage_type == "local":
        # Remove gs:// prefix if present
        if bucket_name.startswith("gs://"):
            bucket_name = bucket_name[5:]

        storage_path = os.getenv("LOCAL_STORAGE_PATH", "./data/storage")
        bucket_path = Path(storage_path) / bucket_name

        bucket_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Local storage directory created: {bucket_path}")

    elif storage_type in ["minio", "s3"]:
        try:
            from minio import Minio

            # Remove gs:// or s3:// prefix if present
            bucket_name = bucket_name.replace("gs://", "").replace("s3://", "")

            endpoint_url = os.getenv("STORAGE_ENDPOINT_URL", "localhost:9000")
            endpoint = endpoint_url.replace("http://", "").replace("https://", "")

            access_key = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
            secret_key = os.getenv("MINIO_SECRET_KEY", "minioadmin")
            secure = os.getenv("MINIO_SECURE", "false").lower() == "true"

            client = Minio(
                endpoint,
                access_key=access_key,
                secret_key=secret_key,
                secure=secure,
            )

            if not client.bucket_exists(bucket_name):
                client.make_bucket(bucket_name)
                logger.info(f"Created MinIO bucket: {bucket_name}")
            else:
                logger.info(f"MinIO bucket already exists: {bucket_name}")

        except Exception as e:
            logger.error(f"Failed to create MinIO bucket: {e}")
            logger.info("Falling back to local directory creation")
            storage_path = os.getenv("LOCAL_STORAGE_PATH", "./data/storage")
            bucket_path = Path(storage_path) / bucket_name
            bucket_path.mkdir(parents=True, exist_ok=True)
