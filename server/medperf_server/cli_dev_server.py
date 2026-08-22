import os

from medperf_server import cli_certs, cli_db, cli_postgres


def start_server(
    cert_file: str,
    key_file: str,
    generate_cert: bool,
    reset_db: bool,
    postgres: bool,
    container_name: str,
) -> None:
    if postgres:
        if reset_db:
            # reset_db's postgres path already recreates the container below;
            # ensuring it running here first would just be undone immediately.
            pass
        else:
            just_started = cli_postgres.ensure_running(container_name)
            if just_started:
                cli_postgres.wait_for_postgres()
            cli_postgres.set_postgres_database_url()

    if reset_db:
        cli_db.reset_database(postgres, container_name)

    if generate_cert:
        cli_certs.generate_cert(cert_file, key_file)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "medperf_server.settings")
    from django.core.management import execute_from_command_line

    execute_from_command_line(["medperf-server", "migrate"])
    execute_from_command_line(["medperf-server", "collectstatic", "--noinput"])
    execute_from_command_line(
        [
            "medperf-server",
            "runserver_plus",
            "--cert-file",
            cert_file,
            "--key-file",
            key_file,
        ]
    )
