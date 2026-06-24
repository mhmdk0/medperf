from rest_framework import status

from medperf.tests import MedPerfTest
from benchmark.models import Benchmark


class CommitteeMembersTest(MedPerfTest):
    def setUp(self):
        super().setUp()
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

        self.bmk_owner = bmk_owner
        self.committee_user = committee_user
        self.url_template = self.api_prefix + "/benchmarks/{0}/"

        _, _, _, testbenchmark = self.shortcut_create_benchmark(
            prep_mlcube_owner,
            ref_model_owner,
            eval_mlcube_owner,
            bmk_owner,
            target_approval_status="PENDING",
            state="DEVELOPMENT",
        )
        self.testbenchmark = testbenchmark
        self.benchmark_obj = Benchmark.objects.get(pk=testbenchmark["id"])

    def test_owner_can_add_committee_member(self):
        # Arrange
        self.set_credentials(self.bmk_owner)
        url = self.url_template.format(self.testbenchmark["id"])
        committee_email = f"{self.committee_user}@example.com"

        # Act
        response = self.client.put(
            url, {"committee_member_emails": [committee_email]}, format="json"
        )

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["committee_member_emails"], [committee_email])
        self.benchmark_obj.refresh_from_db()
        self.assertTrue(
            self.benchmark_obj.committee_members.filter(email=committee_email).exists()
        )

    def test_duplicate_committee_member_emails_are_deduplicated(self):
        # Arrange
        self.set_credentials(self.bmk_owner)
        url = self.url_template.format(self.testbenchmark["id"])
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
        self.benchmark_obj.refresh_from_db()
        self.assertEqual(self.benchmark_obj.committee_members.count(), 1)

    def test_committee_member_can_update_benchmark(self):
        # Arrange
        self.add_benchmark_committee_member(
            self.testbenchmark["id"], self.committee_user
        )
        self.set_credentials(self.committee_user)
        url = self.url_template.format(self.testbenchmark["id"])

        # Act
        response = self.client.put(
            url, {"description": "updated by committee"}, format="json"
        )

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["description"], "updated by committee")

    def test_owner_can_remove_committee_member(self):
        # Arrange
        committee_email = f"{self.committee_user}@example.com"
        self.add_benchmark_committee_member(
            self.testbenchmark["id"], self.committee_user
        )
        self.set_credentials(self.bmk_owner)
        url = self.url_template.format(self.testbenchmark["id"])

        # Act
        response = self.client.put(
            url, {"committee_member_emails": []}, format="json"
        )

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["committee_member_emails"], [])
        self.benchmark_obj.refresh_from_db()
        self.assertEqual(self.benchmark_obj.committee_members.count(), 0)

    def test_add_nonexistent_user_fails(self):
        # Arrange
        self.set_credentials(self.bmk_owner)
        url = self.url_template.format(self.testbenchmark["id"])

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
        url = self.url_template.format(self.testbenchmark["id"])
        owner_email = f"{self.bmk_owner}@example.com"

        # Act
        response = self.client.put(
            url, {"committee_member_emails": [owner_email]}, format="json"
        )

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.benchmark_obj.refresh_from_db()
        self.assertEqual(self.benchmark_obj.committee_members.count(), 0)
