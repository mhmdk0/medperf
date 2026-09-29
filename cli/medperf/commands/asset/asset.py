import typer
from typing import Optional

from medperf.decorators import clean_except
from medperf.entities.asset import Asset
from medperf.commands.list import EntityList
from medperf.commands.view import EntityView
import medperf.help_texts as help_texts

app = typer.Typer()


@app.command("ls")
@clean_except
def list(
    unregistered: bool = typer.Option(
        False, "--unregistered", help=help_texts.asset.ls_unregistered
    ),
    mine: bool = typer.Option(False, "--mine", help=help_texts.asset.ls_mine),
    name: str = typer.Option(None, "--name", "-n", help=help_texts.asset.name_filter),
    owner: int = typer.Option(None, "--owner", help=help_texts.common.owner_filter),
    state: str = typer.Option(None, "--state", help=help_texts.common.state_filter),
):
    """List assets"""
    EntityList.run(
        Asset,
        fields=["UID", "Name", "State", "Registered"],
        unregistered=unregistered,
        mine_only=mine,
        name=name,
        owner=owner,
        state=state,
    )


@app.command("view")
@clean_except
def view(
    entity_id: Optional[int] = typer.Argument(None, help=help_texts.asset.id),
    format: str = typer.Option(
        "yaml",
        "-f",
        "--format",
        help=help_texts.common.format,
    ),
    unregistered: bool = typer.Option(
        False,
        "--unregistered",
        help=help_texts.asset.view_unregistered,
    ),
    mine: bool = typer.Option(
        False,
        "--mine",
        help=help_texts.asset.view_mine,
    ),
    output: str = typer.Option(
        None,
        "--output",
        "-o",
        help=help_texts.common.output,
    ),
):
    """Displays the information of one or more assets"""
    EntityView.run(entity_id, Asset, format, unregistered, mine, output)
