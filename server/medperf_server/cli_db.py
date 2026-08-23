import os
from pathlib import Path

import django
from django.conf import settings
from django.core.management import execute_from_command_line

from medperf_server import cli_postgres


def reset_database(postgres: bool, container_name: str) -> None:
    if postgres:
        cli_postgres.recreate_container(container_name)
        cli_postgres.wait_for_postgres()
        cli_postgres.set_postgres_database_url()

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "medperf_server.settings")
    django.setup()

    if not postgres:
        db_file = Path(settings.DATABASES["default"]["NAME"])
        if db_file.exists():
            db_file.unlink()
        else:
            print(f"warning: {db_file} does not exist, nothing to delete")

    execute_from_command_line(["medperf-server", "migrate"])
