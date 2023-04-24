#!/usr/bin/env sh

set -e

case "$1" in
    app)
        exec python market.py
        ;;
    *)
        exec "$@"
esac