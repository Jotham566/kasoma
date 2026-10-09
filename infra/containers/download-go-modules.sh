#!/bin/sh
# Retry downloads with Go checksum enforcement; final verification failure is terminal.
set -eu
trap 'exit 130' INT
trap 'exit 143' TERM

attempt=1
while [ "$attempt" -le 3 ]; do
    if go mod download; then
        exec go mod verify
    fi
    if [ "$attempt" -eq 3 ]; then
        echo 'Module download failed after three attempts.' >&2
        exit 1
    fi
    echo 'Module download incomplete; retrying pinned dependencies.' >&2
    attempt=$((attempt + 1))
done
