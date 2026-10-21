from medperf.exceptions import InvalidArgumentError, CleanExit
import pytest
from medperf.tests.mocks import TestCube
from medperf.tests.mocks.benchmark import TestBenchmark
from medperf.tests.mocks.dataset import TestDataset
from medperf.commands.dataset.submit import DataCreation
from medperf.entities.dataset import Dataset

PATCH_DATAPREP = "medperf.commands.dataset.submit.{}"
OUT_PATH = "out_path"
STATISTICS_PATH = "statistics_path"
OUT_DATAPATH = "out_path/data"
OUT_LABELSPATH = "out_path/labels"
BENCHMARK_UID = "benchmark_uid"
DATA_PATH = "data_path"
LABELS_PATH = "labels_path"
METADATA_PATH = "metadata"
NAME = "name"
DESCRIPTION = "description"
LOCATION = "location"
SUMMARY_PATH = "summary"
REPORT_PATH = "report"
IS_PREPARED = False


@pytest.fixture
def creation(mocker, comms, ui):
    mocker.patch(PATCH_DATAPREP.format("Benchmark.get"), return_value=TestBenchmark())
    creation = DataCreation(
        BENCHMARK_UID,
        None,
        DATA_PATH,
        LABELS_PATH,
        None,
        NAME,
        DESCRIPTION,
        LOCATION,
        False,
        IS_PREPARED,
        for_test=False,
    )
    mocker.patch(
        PATCH_DATAPREP.format("Cube.get"), return_value=TestCube(is_valid=True)
    )
    creation.data_path = DATA_PATH
    creation.labels_path = LABELS_PATH
    return creation


class TestWithDefaultUID:
    @pytest.mark.parametrize("data_exists", [True, False])
    @pytest.mark.parametrize("labels_exist", [True, False])
    def test_validate_fails_when_paths_dont_exist(
        self, mocker, creation, data_exists, labels_exist, fs
    ):
        if data_exists:
            fs.create_dir(DATA_PATH)
        if labels_exist:
            fs.create_dir(LABELS_PATH)

        should_fail = not data_exists or not labels_exist

        # Act & Assert
        if should_fail:
            with pytest.raises(InvalidArgumentError):
                creation.validate()
        else:
            creation.validate()

    @pytest.mark.parametrize("cube_uid", [1776, 4342, 573])
    def test_validate_prep_cube_gets_prep_cube_if_provided(
        self, mocker, cube_uid, comms, ui, fs
    ):
        # Arrange
        spy = mocker.patch(
            PATCH_DATAPREP.format("Cube.get"), return_value=TestCube(is_valid=True)
        )

        # Act
        creation = DataCreation(
            None, cube_uid, "", "", None, "", "", "", False, False, False
        )
        creation.validate_prep_cube()

        # Assert
        spy.assert_called_once_with(cube_uid)

    @pytest.mark.parametrize("cube_uid", [998, 68, 109])
    def test_validate_prep_cube_gets_benchmark_cube_if_provided(
        self, mocker, cube_uid, comms, ui, fs
    ):
        # Arrange
        benchmark = TestBenchmark(data_preparation_mlcube=cube_uid)
        mocker.patch(PATCH_DATAPREP.format("Benchmark.get"), return_value=benchmark)
        spy = mocker.patch(
            PATCH_DATAPREP.format("Cube.get"), return_value=TestCube(is_valid=True)
        )

        # Act
        creation = DataCreation(
            cube_uid, None, "", "", None, "", "", "", False, False, False
        )
        creation.validate_prep_cube()

        # Assert
        spy.assert_called_once_with(cube_uid)

    @pytest.mark.parametrize("benchmark_uid", [None, 1])
    @pytest.mark.parametrize("cube_uid", [None, 1])
    def test_fails_if_invalid_params(self, mocker, benchmark_uid, cube_uid, comms, ui):
        # Arrange
        num_arguments = int(benchmark_uid is None) + int(cube_uid is None)

        # Act
        creation = DataCreation(
            benchmark_uid, cube_uid, "", "", None, "", "", "", False, False, False
        )
        # Assert

        if num_arguments != 1:
            with pytest.raises(InvalidArgumentError):
                creation.validate()

        else:
            creation.validate()

    def test_write_calls_dataset_write(self, mocker, creation):
        # Arrange
        data_dict = TestDataset().todict()
        spy = mocker.patch(PATCH_DATAPREP.format("Dataset.write"))
        # Act
        creation.write(data_dict)

        # Assert
        spy.assert_called_once()

    @pytest.mark.parametrize("exists", [True, False])
    @pytest.mark.parametrize("uid", [858, 2770, 2052])
    @pytest.mark.parametrize("old_uid", ["generated_uid", "3749badff"])
    def test_to_permanent_path_renames_folder_correctly(
        self, mocker, creation, exists, old_uid, uid
    ):
        # Arrange
        old_dset = TestDataset(id=None, generated_uid=old_uid)
        new_dset = TestDataset(id=uid)
        rename_spy = mocker.patch("os.rename")
        cleanup_spy = mocker.patch(PATCH_DATAPREP.format("remove_path"))
        mocker.patch("os.path.exists", return_value=exists)
        creation.dataset = old_dset
        old_path = Dataset(**old_dset.todict()).path
        new_path = Dataset(**new_dset.todict()).path

        # Act
        creation.to_permanent_path(new_dset.todict())

        # Assert
        cleanup_spy.assert_called_once_with(new_path)
        rename_spy.assert_called_once_with(old_path, new_path)


class TestPublicDataset:
    DATA_URL = "https://example.com/data.tar.gz"
    TMP_PATH = "/tmp_dataset"

    @pytest.fixture
    def public_creation(self, creation):
        creation.data_path = None
        creation.labels_path = None
        creation.data_url = self.DATA_URL
        return creation

    def test_validate_fails_if_url_and_paths_are_provided(self, creation):
        # Arrange
        creation.data_url = self.DATA_URL

        # Act & Assert
        with pytest.raises(InvalidArgumentError):
            creation.validate()

    def test_validate_fails_if_neither_url_nor_paths_are_provided(self, creation):
        # Arrange
        creation.data_path = None
        creation.labels_path = None

        # Act & Assert
        with pytest.raises(InvalidArgumentError):
            creation.validate()

    def test_validate_passes_with_url_only(self, public_creation):
        public_creation.validate()

    @pytest.mark.parametrize("data_exists", [True, False])
    @pytest.mark.parametrize("labels_exist", [True, False])
    def test_get_public_data_checks_tarball_layout(
        self, mocker, public_creation, data_exists, labels_exist, fs
    ):
        # Arrange
        mocker.patch(
            PATCH_DATAPREP.format("generate_tmp_path"), return_value=self.TMP_PATH
        )
        mocker.patch(
            PATCH_DATAPREP.format("download_resource"), return_value="tarball_hash"
        )
        untar_spy = mocker.patch(PATCH_DATAPREP.format("untar"))
        if data_exists:
            fs.create_dir(f"{self.TMP_PATH}/data")
        if labels_exist:
            fs.create_dir(f"{self.TMP_PATH}/labels")

        # Act & Assert
        if data_exists and labels_exist:
            public_creation.get_public_data()
            untar_spy.assert_called_once()
            assert public_creation.asset_hash == "tarball_hash"
            assert public_creation.data_path == f"{self.TMP_PATH}/data"
            assert public_creation.labels_path == f"{self.TMP_PATH}/labels"
        else:
            with pytest.raises(InvalidArgumentError):
                public_creation.get_public_data()

    def test_create_dataset_object_creates_public_asset(
        self, mocker, public_creation, fs
    ):
        # Arrange
        mocker.patch(PATCH_DATAPREP.format("get_folders_hash"), return_value="in_uid")
        raw_paths_spy = mocker.patch(PATCH_DATAPREP.format("Dataset.set_raw_paths"))
        public_creation.prep_cube_uid = 1
        public_creation.asset_hash = "tarball_hash"

        # Act
        public_creation.create_dataset_object()

        # Assert
        dataset = public_creation.dataset
        assert dataset.input_data_hash == "in_uid"
        assert dataset.asset.name == NAME
        assert dataset.asset.asset_url == self.DATA_URL
        assert dataset.asset.asset_hash == "tarball_hash"
        assert dataset.is_public()
        raw_paths_spy.assert_not_called()

    def test_run_does_not_copy_public_data_when_submitted_as_prepared(
        self, mocker, comms, ui
    ):
        # Arrange
        mocker.patch(PATCH_DATAPREP.format("DataCreation.validate"))
        mocker.patch(PATCH_DATAPREP.format("DataCreation.validate_prep_cube"))
        get_data_spy = mocker.patch(PATCH_DATAPREP.format("DataCreation.get_public_data"))
        mocker.patch(PATCH_DATAPREP.format("DataCreation.create_dataset_object"))
        prepared_spy = mocker.patch(
            PATCH_DATAPREP.format("DataCreation.make_dataset_prepared")
        )
        mocker.patch(PATCH_DATAPREP.format("DataCreation.upload"), return_value={"id": 1})
        mocker.patch(PATCH_DATAPREP.format("DataCreation.to_permanent_path"))
        mocker.patch(PATCH_DATAPREP.format("DataCreation.write"))

        # Act
        DataCreation.run(
            "", 1, None, None, None, "", "", "", False,
            submit_as_prepared=True, data_url=self.DATA_URL,
        )

        # Assert
        get_data_spy.assert_called_once()
        prepared_spy.assert_not_called()


def test_create_dataset_object_creates_local_asset(mocker, creation, fs):
    # Arrange
    mocker.patch(PATCH_DATAPREP.format("get_folders_hash"), return_value="in_uid")
    raw_paths_spy = mocker.patch(PATCH_DATAPREP.format("Dataset.set_raw_paths"))
    creation.prep_cube_uid = 1

    # Act
    creation.create_dataset_object()

    # Assert
    dataset = creation.dataset
    assert dataset.asset.name == NAME
    assert dataset.asset.asset_url == "local"
    assert dataset.asset.asset_hash == "in_uid"
    assert not dataset.is_public()
    raw_paths_spy.assert_called_once_with(
        raw_data_path=DATA_PATH, raw_labels_path=LABELS_PATH
    )


@pytest.mark.parametrize("uid", [67342, 236, 1570])
def test_run_returns_generated_uid(mocker, comms, ui, uid):
    # Arrange
    mocker.patch(PATCH_DATAPREP.format("DataCreation.validate"))
    mocker.patch(PATCH_DATAPREP.format("DataCreation.validate_prep_cube"))
    mocker.patch(PATCH_DATAPREP.format("DataCreation.create_dataset_object"))
    mocker.patch(PATCH_DATAPREP.format("DataCreation.upload"), return_value={"id": uid})
    mocker.patch(
        PATCH_DATAPREP.format("DataCreation.to_permanent_path"),
    )
    mocker.patch(
        PATCH_DATAPREP.format("DataCreation.write"),
    )
    mocker.patch(
        PATCH_DATAPREP.format("Cube.get"),
        side_effect=lambda id: TestCube(is_valid=True, id=id),
    )

    # Act
    returned_uid = DataCreation.run("", 1, "", "", None, "", "", "", False)

    # Assert
    assert returned_uid == uid


@pytest.mark.parametrize("approved", [True, False])
class TestWithApproval:
    def test_run_uploads_dataset_if_approved(
        self, mocker, comms, ui, creation, approved
    ):
        # Arrange
        mocker.patch(
            PATCH_DATAPREP.format("approval_prompt"),
            return_value=approved,
        )
        dataset = TestDataset()
        mocker.patch(PATCH_DATAPREP.format("Dataset"), return_value=dataset)
        mocker.patch(PATCH_DATAPREP.format("Dataset.write"))
        spy = mocker.patch.object(dataset, "upload")
        mocker.patch("os.rename")

        # Act
        if approved:
            DataCreation.run("", 1, "", "", None, "", "", "", False)

            # Assert
            spy.assert_called_once()
        else:
            with pytest.raises(CleanExit):
                DataCreation.run("", 1, *[""] * 2)

            spy.assert_not_called()

    def test_skips_request_approval_if_preapproved(self, mocker, comms, ui, approved):
        # Arrange
        spy = mocker.patch(
            PATCH_DATAPREP.format("approval_prompt"),
            return_value=True,
        )
        mocker.patch(PATCH_DATAPREP.format("Dataset.write"))
        mocker.patch("os.rename")
        dataset = TestDataset()
        mocker.patch.object(dataset, "set_raw_paths")
        mocker.patch(PATCH_DATAPREP.format("Dataset"), return_value=dataset)
        mocker.patch(
            PATCH_DATAPREP.format("Cube.get"),
            side_effect=lambda id: TestCube(is_valid=True, id=id),
        )

        # Act
        DataCreation.run("", 1, *[""] * 2, approved=approved)

        # Assert
        if approved:
            spy.assert_not_called()
        else:
            spy.assert_called_once()
