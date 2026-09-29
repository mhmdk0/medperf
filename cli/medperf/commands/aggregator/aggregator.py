from typing import Optional
from medperf.entities.aggregator import Aggregator
import typer

import medperf.config as config
from medperf.decorators import clean_except
from medperf.commands.aggregator.submit import SubmitAggregator
from medperf.commands.aggregator.run import StartAggregator

from medperf.commands.list import EntityList
from medperf.commands.view import EntityView
import medperf.help_texts as help_texts

app = typer.Typer()


@app.command("submit")
@clean_except
def submit(
    name: str = typer.Option(..., "--name", "-n", help=help_texts.aggregator.name),
    address: str = typer.Option(
        ..., "--address", "-a", help=help_texts.aggregator.address
    ),
    port: int = typer.Option(..., "--port", "-p", help=help_texts.aggregator.port),
    admin_port: int = typer.Option(
        ...,
        "--admin-port",
        help=help_texts.aggregator.admin_port,
    ),
    aggregation_mlcube: int = typer.Option(
        ...,
        "--aggregation-container",
        "-m",
        help=help_texts.aggregator.aggregation_container,
    ),
):
    """Submits an aggregator"""
    SubmitAggregator.run(name, address, port, admin_port, aggregation_mlcube)
    config.ui.print("✅ Done!")


@app.command("start")
@clean_except
def run(
    training_exp_id: int = typer.Option(
        ...,
        "--training_exp_id",
        "-t",
        help=help_texts.aggregator.start_training_exp_id,
    ),
    publish_on: str = typer.Option(
        "127.0.0.1",
        "--publish_on",
        "-p",
        help=help_texts.aggregator.publish_on,
    ),
    overwrite: bool = typer.Option(
        False, "--overwrite", help=help_texts.common.overwrite
    ),
):
    """Starts the aggregation server of a training experiment"""
    StartAggregator.run(training_exp_id, publish_on, overwrite)
    config.ui.print("✅ Done!")


@app.command("ls")
@clean_except
def list(
    unregistered: bool = typer.Option(
        False, "--unregistered", help=help_texts.aggregator.ls_unregistered
    ),
    mine: bool = typer.Option(False, "--mine", help=help_texts.aggregator.ls_mine),
):
    """List aggregators"""
    EntityList.run(
        Aggregator,
        fields=["UID", "Name", "Address", "Port"],
        unregistered=unregistered,
        mine_only=mine,
    )


@app.command("view")
@clean_except
def view(
    entity_id: Optional[int] = typer.Argument(None, help=help_texts.aggregator.id),
    format: str = typer.Option(
        "yaml",
        "-f",
        "--format",
        help=help_texts.common.format,
    ),
    unregistered: bool = typer.Option(
        False,
        "--unregistered",
        help=help_texts.aggregator.view_unregistered,
    ),
    mine: bool = typer.Option(
        False,
        "--mine",
        help=help_texts.aggregator.view_mine,
    ),
    output: str = typer.Option(
        None,
        "--output",
        "-o",
        help=help_texts.common.output,
    ),
):
    """Displays the information of one or more aggregators"""
    EntityView.run(entity_id, Aggregator, format, unregistered, mine, output)
