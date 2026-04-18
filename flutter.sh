#!/usr/bin/env bash
# Flutter wrapper using puro-installed Flutter SDK
DART_EXE="$HOME/.puro/shared/caches/425cfb54d01a9472b3e81d9e76fd63a4a44cfbcb/dart-sdk/bin/dart.exe"
FLUTTER_TOOLS="$HOME/.puro/envs/stable/flutter/packages/flutter_tools"
CACHE_DIR="$HOME/.puro/envs/stable/flutter/bin/cache"
SNAPSHOT="$CACHE_DIR/flutter_tools.snapshot"
PKG_CONFIG="$FLUTTER_TOOLS/.dart_tool/package_config.json"
export FLUTTER_ROOT="$HOME/.puro/envs/stable/flutter"

"$DART_EXE" --packages="$PKG_CONFIG" "$SNAPSHOT" "$@"
