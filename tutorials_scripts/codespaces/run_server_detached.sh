#!/usr/bin/env bash
cd /workspaces/medperf/server
medperf_server start < /dev/null &>server.log &
