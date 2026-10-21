from django.db import migrations
from django.db.backends.postgresql.schema import DatabaseSchemaEditor
from django.db.migrations.state import StateApps

ASSET_NAME_MAX_LENGTH = 128


def get_unique_asset_name(Asset, dataset) -> str:
    # Asset names are globally unique while dataset names are not,
    # so a suffix with the dataset id is added in case of a collision.
    name = dataset.name
    counter = 0
    while Asset.objects.filter(name=name).exists():
        suffix = f"_{dataset.id}" if counter == 0 else f"_{dataset.id}_{counter}"
        name = dataset.name[: ASSET_NAME_MAX_LENGTH - len(suffix)] + suffix
        counter += 1
    return name


def createassetsfromdatasets(
    apps: StateApps, schema_editor: DatabaseSchemaEditor
) -> None:
    Dataset = apps.get_model("dataset", "Dataset")
    Asset = apps.get_model("asset", "Asset")

    # All existing datasets are private, so they are backed by local assets
    for dataset in Dataset.objects.filter(asset__isnull=True).order_by("id"):
        asset = Asset.objects.create(
            name=get_unique_asset_name(Asset, dataset),
            owner=dataset.owner,
            asset_hash=dataset.input_data_hash,
            asset_url="local",
            state=dataset.state,
            is_valid=dataset.is_valid,
        )
        dataset.asset = asset
        dataset.save(update_fields=["asset"])


def removeassetsfromdatasets(
    apps: StateApps, schema_editor: DatabaseSchemaEditor
) -> None:
    Dataset = apps.get_model("dataset", "Dataset")

    for dataset in Dataset.objects.filter(asset__isnull=False):
        asset = dataset.asset
        dataset.asset = None
        dataset.save(update_fields=["asset"])
        asset.delete()


class Migration(migrations.Migration):
    dependencies = [
        ("dataset", "0007_dataset_asset"),
    ]
    operations = [
        migrations.RunPython(createassetsfromdatasets, removeassetsfromdatasets)
    ]
