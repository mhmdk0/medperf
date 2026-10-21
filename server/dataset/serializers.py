from rest_framework import serializers
from .models import Dataset
from user.serializers import UserSerializer
from asset.serializers import AssetSerializer
from asset.models import Asset
from django.db import transaction


class DatasetFullSerializer(serializers.ModelSerializer):
    """A private serializer. used for users who are permitted to see
    "sensitive" information. This serializer is also used for POST"""

    asset = AssetSerializer()

    class Meta:
        model = Dataset
        fields = "__all__"
        read_only_fields = ["owner", "state"]

    def validate(self, attrs):
        asset = attrs["asset"]

        state = attrs.get("state", "DEVELOPMENT")
        asset_state = asset.get("state", "DEVELOPMENT")
        if state != asset_state:
            raise serializers.ValidationError(
                "Dataset state must match the state of its asset."
            )

        is_valid = attrs.get("is_valid", True)
        asset_is_valid = asset.get("is_valid", True)
        if is_valid != asset_is_valid:
            raise serializers.ValidationError(
                "Dataset validity must match the validity of its asset."
            )
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        asset_data = validated_data.pop("asset")
        asset = Asset.objects.create(**asset_data, owner=validated_data["owner"])
        validated_data["asset"] = asset
        return Dataset.objects.create(**validated_data)


class DatasetPublicSerializer(serializers.ModelSerializer):
    """A restrictive serializer"""

    asset = AssetSerializer(read_only=True)

    class Meta:
        model = Dataset
        exclude = ["report"]


class DatasetDetailSerializer(serializers.ModelSerializer):
    """This is a private serializer like DatasetFullSerializer"""

    asset = AssetSerializer(read_only=True)

    class Meta:
        model = Dataset
        fields = "__all__"
        read_only_fields = ["owner"]

    def _validate_guid(self, data):
        # NOTE: this is checking the uniqueness of generated_uid across
        #       operational datasets. This check relies on the fact that
        #       such a constraint can only be violated by updating the state.
        #       updating the generated_uid while state is OPERATION is already
        #       not allowed.
        # NOTE: This is written explicitely although the constraint is also
        #       defined in models.py. The reason is that DRF doesn't translate
        #       uniqueness constraint correctly, causing a 500 server error
        #       if the check was left to be done by the database.
        if (
            data.get("state")
            and data["state"] == "OPERATION"
            and self.instance.state == "DEVELOPMENT"
        ):
            constraint = (
                Dataset.objects.all()
                .filter(
                    state="OPERATION",
                    generated_uid=data.get(
                        "generated_uid", self.instance.generated_uid
                    ),
                )
                .exists()
            )
            if constraint:
                raise serializers.ValidationError(
                    "An Operational dataset with the same "
                    "generated UID already exists"
                )

    def validate(self, data):
        if self.instance.state == "OPERATION":
            editable_fields = ["is_valid", "user_metadata"]
            for k, v in data.items():
                value_changed = v != getattr(self.instance, k)
                if k not in editable_fields and value_changed:
                    raise serializers.ValidationError(
                        "User cannot update non editable fields in Operation mode"
                    )
        self._validate_guid(data)

        return data

    @transaction.atomic
    def update(self, instance, validated_data):
        asset = instance.asset
        asset.state = validated_data.get("state", asset.state)
        asset.is_valid = validated_data.get("is_valid", asset.is_valid)
        if asset.asset_url == "local":
            # A local asset is identified by the hash of the raw data
            asset.asset_hash = validated_data.get(
                "input_data_hash", asset.asset_hash
            )
        asset.save()

        return super().update(instance, validated_data)


class DatasetWithOwnerInfoSerializer(serializers.ModelSerializer):
    """This is needed when getting datasets and their owners
    with one API call."""

    owner = UserSerializer()

    class Meta:
        model = Dataset
        fields = ["id", "owner"]
