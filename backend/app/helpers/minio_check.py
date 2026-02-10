from obstore.store import S3Store
from app.core.config import get_settings

_settings = get_settings()


def minio_check():
    store = S3Store(
            _settings.MINIO_BUCKET,
            endpoint=_settings.MINIO_ENDPOINT,
            access_key_id=_settings.MINIO_ACCESS_KEY,
            secret_access_key=_settings.MINIO_SECRET_KEY,
            virtual_hosted_style_request=False,
            client_options={"allow_http": True},
        )

    return store

