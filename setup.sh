#!/bin/bash
# This file is part of Scanarium https://scanarium.com/ and licensed under the
# GNU Affero General Public License v3.0 (See LICENSE.md)
# SPDX-License-Identifier: AGPL-3.0-only

set -e
set -o pipefail

cd "$(dirname "$0")"

PHASER_VERSION="3.52.0"
PHASER_TARGET="frontend/phaser-${PHASER_VERSION}.js"
CONF_TARGET="conf/scanarium.conf"
VERBOSITY=0
VERBOSE_ARGS=()

error() {
    echo "ERROR" "$@" >&2
    exit 1
}

step() {
    local NAME="$1"
    local TARGET="$2"
    shift 2

    local HEADER_SUFFIX=""
    if [ "$TARGET" != "@always" ]
    then
        HEADER_SUFFIX="at '$TARGET' "
    fi

    echo
    echo "#################################################################"
    echo "Setting up $NAME $HEADER_SUFFIX..."
    echo

    if [ "$TARGET" = "@always" -o ! -e "$TARGET" ]
    then
        echo "Running:" "$@"
        "$@"
    else
        echo "(Skipping as '$TARGET' already exists)"
    fi
}

generate_global_config() {
  echo "{}" >"dynamic/config.json"
}

generate_command_log() {
  echo "[]" >"dynamic/command-log.json"
}

generate_sample_content() {
    cp -a "dynamic.sample/"* "dynamic"
}

generate_thumbnails() {
    local LOG_COMMAND=""
    if [ "$VERBOSITY" -gt 0 ]
    then
        LOG_COMMAND="print('Generating thumbnail for', full_path)"
    fi
    local FILE=
    while read FILE
    do
        /usr/bin/env python3 - "$FILE" <<EOF
import os
import sys
from scanarium import Scanarium
full_path = sys.argv[1]
$LOG_COMMAND
dir, file = os.path.split(full_path)
Scanarium().generate_thumbnail(dir, file)
EOF
    done < <(find dynamic/scenes/*/actors -iname '*.png' ! -iname '*thumbnail.*')
}

run_setup() {
    step "phaser ${PHASER_VERSION}" "$PHASER_TARGET" curl --output "$PHASER_TARGET" "https://cdn.jsdelivr.net/npm/phaser@${PHASER_VERSION}/dist/phaser.min.js"
    step "example configuration" "$CONF_TARGET" cp "conf/scanarium.conf.example" "$CONF_TARGET"
    step "content directory" "dynamic" mkdir -p "dynamic"
    step "sample content" "dynamic/scenes/space/actors/SimpleRocket/sample.png" generate_sample_content
    step "thumbnails" "@always" generate_thumbnails
    step "global config" "dynamic/config.json" generate_global_config
    step "command log" "dynamic/command-log.json" generate_command_log
    step "static content" "@always" ./regenerate-static-content.sh
    step "content index" "@always" ./reindex.sh

    echo
    echo "#################################################################"
    echo
    echo "All done."
    echo
    echo "Now edit '$CONF_TARGET' to your liking and start Scanarium by running ./run-demo-server.sh"
}


parse_arguments() {
    while [ $# -gt 0 ]
    do
        local ARGUMENT="$1"
        shift
        case "$ARGUMENT" in
            "-v" | "--verbose" )
                VERBOSITY=$((VERBOSITY + 1))
                VERBOSE_ARGS+=("--verbose")
                ;;
            "-vv" )
                parse_arguments "-v" "-v"
                ;;
            "-vvv" )
                parse_arguments "-v" "-v" "-v"
                ;;
            * )
                error "Unknown argument '$ARGUMENT'"
                ;;
        esac
    done
}

parse_arguments "$@"
run_setup
