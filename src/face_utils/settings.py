from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_db: str
    postgres_host: str
    postgres_port: str
    postgres_user: str
    postgres_password: str
    dir_bucket_files_dir: str
    origin_images_bucket_name: str = "origin"
    processed_images_bucket_name: str = "processed"
    job_stream_name: str = "process"
    stream_group_name: str = "process_group"
    ws_stream_name: str = "ws"
    redis_host: str
    redis_port: int
    static_dir: str

    class Config:
        env_file = ".envs"


@lru_cache()
def get_settings():
    return Settings()


SETTINGS = get_settings()


TORTOISE_CONFIG = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.asyncpg",
            "credentials": {
                "user": SETTINGS.postgres_user,
                "host": SETTINGS.postgres_host,
                "port": SETTINGS.postgres_port,
                "database": SETTINGS.postgres_db,
                "password": SETTINGS.postgres_password,
            },
        },
    },
    "apps": {
        "models": {
            "models": ["face_utils.models"],
            "default_connection": "default",
        },
    },
    "use_tz": False,
    "timezone": "Europe/Warsaw",
}
