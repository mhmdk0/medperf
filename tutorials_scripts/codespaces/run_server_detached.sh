#!/usr/bin/env bash
cd /workspaces/medperf/server
export AUTH_VERIFYING_KEY_FILE="$HOME/.medperf_dev/keys/public_key.pem"
bash ./setup-dev-server.sh < /dev/null &>server.log &
