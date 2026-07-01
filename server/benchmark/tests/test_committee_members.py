from rest_framework import status

from medperf.tests import MedPerfTest

from parameterized import parameterized_class


class BenchmarkCommitteeMembersTest(MedPerfTest):
    def generic_setup(self):
        # setup users
        bmk_owner = "bmk_owner"
        prep_mlcube_owner = "prep_mlcube_owner"
        ref_model_owner = "ref_model_owner"
        eval_mlcube_owner = "eval_mlcube_owner"
        committee_user = "committee_user"

        self.create_user(bmk_owner)
        self.create_user(prep_mlcube_owner)
        self.create_user(ref_model_owner)
        self.create_user(eval_mlcube_owner)
        self.create_user(committee_user)

        # create benchmark
        prep, _, _, benchmark = self.shortcut_create_benchmark(
            prep_mlcube_owner,
            ref_model_owner,
            eval_mlcube_owner,
            bmk_owner,
            target_approval_status="PENDING",
            state="DEVELOPMENT",
        )

        # setup globals
        self.bmk_owner = bmk_owner
        self.prep_mlcube_owner = prep_mlcube_owner
        self.ref_model_owner = ref_model_owner
        self.eval_mlcube_owner = eval_mlcube_owner
        self.committee_user = committee_user
        self.benchmark_id = benchmark["id"]
        self.prep_id = prep["id"]
        self.url = self.api_prefix + "/benchmarks/{0}/"
        self.datasets_url = self.api_prefix + "/benchmarks/{0}/datasets/"
        self.models_url = self.api_prefix + "/benchmarks/{0}/models/"
        self.set_credentials(None)


class BenchmarkCommitteeMembersPutTest(BenchmarkCommitteeMembersTest):
    """Test module for PUT /benchmarks/<pk> committee_member_emails"""

    def setUp(self):
        super(BenchmarkCommitteeMembersPutTest, self).setUp()
        self.generic_setup()

    def test_owner_can_add_committee_member(self):
        # Arrange
        self.set_credentials(self.bmk_owner)
        url = self.url.format(self.benchmark_id)
        committee_email = f"{self.committee_user}@example.com"

        # Act
        response = self.client.put(
            url, {"committee_member_emails": [committee_email]}, format="json"
        )

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["committee_member_emails"], [committee_email])

    def test_duplicate_committee_member_emails_are_deduplicated(self):
        # Arrange
        self.set_credentials(self.bmk_owner)
        url = self.url.format(self.benchmark_id)
        committee_email = f"{self.committee_user}@example.com"

        # Act
        response = self.client.put(
            url,
            {"committee_member_emails": [committee_email, committee_email]},
            format="json",
        )

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["committee_member_emails"], [committee_email])

    def test_owner_can_remove_committee_member(self):
        # Arrange
        committee_email = f"{self.committee_user}@example.com"
        self.add_benchmark_committee_member(self.benchmark_id, self.committee_user)
        self.set_credentials(self.bmk_owner)
        url = self.url.format(self.benchmark_id)
        response = self.client.get(url)
        self.assertEqual(response.data["committee_member_emails"], [committee_email])

        # Act
        response = self.client.put(url, {"committee_member_emails": []}, format="json")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["committee_member_emails"], [])

    def test_add_nonexistent_user_fails(self):
        # Arrange
        self.set_credentials(self.bmk_owner)
        url = self.url.format(self.benchmark_id)

        # Act
        response = self.client.put(
            url,
            {"committee_member_emails": ["missing@example.com"]},
            format="json",
        )

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_owner_cannot_be_committee_member(self):
        # Arrange
        self.set_credentials(self.bmk_owner)
        url = self.url.format(self.benchmark_id)
        owner_email = f"{self.bmk_owner}@example.com"

        # Act
        response = self.client.put(
            url, {"committee_member_emails": [owner_email]}, format="json"
        )

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.get(url)
        self.assertEqual(response.data["committee_member_emails"], [])


@parameterized_class(
    [
        {"actor": "committee_user"},
    ]
)
class BenchmarkCommitteeMemberAccessTest(BenchmarkCommitteeMembersTest):
    """Test module for committee member access to /benchmarks/<pk>"""

    def setUp(self):
        super(BenchmarkCommitteeMemberAccessTest, self).setUp()
        self.generic_setup()
        self.add_benchmark_committee_member(self.benchmark_id, self.committee_user)
        self.set_credentials(self.actor)

    def test_committee_member_can_get_private_benchmark_fields(self):
        # Arrange
        url = self.url.format(self.benchmark_id)

        # Act
        response = self.client.get(url)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for field in [
            "committee_member_emails",
            "dataset_auto_approval_allow_list",
            "model_auto_approval_allow_list",
        ]:
            self.assertIn(field, response.data)

    def test_committee_member_can_update_benchmark(self):
        # Arrange
        url = self.url.format(self.benchmark_id)

        # Act
        response = self.client.put(
            url, {"description": "updated by committee"}, format="json"
        )

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["description"], "updated by committee")


@parameterized_class(
    [
        {"actor": "committee_user"},
    ]
)
class BenchmarkCommitteeMemberAssociationsAccessTest(BenchmarkCommitteeMembersTest):
    """Test module for committee member access to benchmark associations"""

    def setUp(self):
        super(BenchmarkCommitteeMemberAssociationsAccessTest, self).setUp()
        self.generic_setup()

        self.set_credentials("api_admin")
        self.client.put(
            self.url.format(self.benchmark_id),
            {"approval_status": "APPROVED"},
            format="json",
        )
        self.add_benchmark_committee_member(self.benchmark_id, self.committee_user)

        data_owner = "data_owner"
        self.create_user(data_owner)
        dataset = self.mock_dataset(
            data_preparation_mlcube=self.prep_id,
            generated_uid="dataset1",
            state="OPERATION",
        )
        self.set_credentials(data_owner)
        dataset = self.create_dataset(dataset).data
        assoc = self.mock_dataset_association(
            self.benchmark_id, dataset["id"], approval_status="APPROVED"
        )
        self.create_dataset_association(assoc, data_owner, self.bmk_owner)

        model_owner = "model_owner"
        self.create_user(model_owner)
        model = self.mock_model(
            name="committee_model1",
            container_config={"committee_model1": "committee_model1"},
            state="OPERATION",
        )
        self.set_credentials(model_owner)
        model = self.create_model(model).data
        assoc = self.mock_model_association(
            self.benchmark_id, model["id"], approval_status="APPROVED"
        )
        self.create_model_association(assoc, model_owner, self.bmk_owner)

        self.set_credentials(self.actor)

    def test_committee_member_can_get_datasets_list(self):
        # Arrange
        url = self.datasets_url.format(self.benchmark_id)

        # Act
        response = self.client.get(url)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_committee_member_can_get_models_list(self):
        # Arrange
        url = self.models_url.format(self.benchmark_id)

        # Act
        response = self.client.get(url)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
