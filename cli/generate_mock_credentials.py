"""Generates local mock login credentials (keypair + signed tokens) for
Medperf CLI's local/testauth test profiles, if they don't already exist yet.

Used by CI workflows and dev tooling to populate ~/.medperf_dev before
starting a local dev server, so the server can be pointed at the same
keypair via AUTH_VERIFYING_KEY_FILE."""

from medperf.comms.auth.local import Local

if __name__ == "__main__":
    Local.ensure_mock_credentials()
