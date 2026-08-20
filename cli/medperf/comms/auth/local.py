from medperf.comms.auth.interface import Auth
import medperf.config as config
from medperf.exceptions import InvalidArgumentError
from medperf.account_management import (
    set_credentials,
    read_credentials,
    delete_credentials,
)
from medperf.mock_tokens.generate_keypair import generate_keypair
from medperf.mock_tokens.generate_tokens import generate_tokens
import json
import os


class Local(Auth):
    def __init__(self):
        self.ensure_mock_credentials()
        with open(config.local_tokens_path) as f:
            self.tokens = json.load(f)

    @staticmethod
    def ensure_mock_credentials():
        """Generates the local mock login keypair and tokens.json, if either
        is missing yet. Called on Local() first use, and directly by CI/dev
        tooling (see cli/generate_mock_credentials.py) to bootstrap
        ~/.medperf_dev before a local dev server starts.
        """
        if not os.path.exists(config.local_private_key_path):
            Local._generate_keypair()
        if not os.path.exists(config.local_tokens_path):
            Local._generate_tokens_file()

    @staticmethod
    def _generate_keypair():
        """Generates a fresh keypair for signing local login tokens.

        A local dev server must be pointed at config.local_public_key_path
        (e.g. via AUTH_VERIFYING_KEY_FILE) to trust tokens signed with it.
        """
        private_key_pem, public_key_pem = generate_keypair()
        os.makedirs(config.local_keys_dir, exist_ok=True)
        with open(config.local_private_key_path, "wb") as f:
            f.write(private_key_pem)
        with open(config.local_public_key_path, "wb") as f:
            f.write(public_key_pem)

    @staticmethod
    def _generate_tokens_file():
        with open(config.local_private_key_path, "rb") as f:
            private_key_pem = f.read()
        tokens = generate_tokens(private_key_pem)
        os.makedirs(os.path.dirname(config.local_tokens_path), exist_ok=True)
        with open(config.local_tokens_path, "w") as f:
            json.dump(tokens, f)

    def login(self, email):
        """Retrieves and stores an access token from a local store json file.

        Args:
            email (str): user email.
        """

        try:
            access_token = self.tokens[email]
        except KeyError:
            raise InvalidArgumentError(
                "The provided email does not exist for testing. "
                "Make sure you activated the right profile."
            )
        refresh_token = "refresh token"
        id_token_payload = {"email": email}
        token_issued_at = 0
        token_expires_in = 10**10

        set_credentials(
            access_token,
            refresh_token,
            id_token_payload,
            token_issued_at,
            token_expires_in,
            login_event=True,
        )

    def logout(self):
        """Logs out the user by deleting the stored tokens."""
        delete_credentials()

    @property
    def access_token(self):
        """Reads and returns an access token of the currently logged
        in user to be used for authorizing requests to the MedPerf server.

        Returns:
            access_token (str): the access token
        """

        creds = read_credentials()
        access_token = creds["access_token"]
        return access_token
