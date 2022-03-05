#!/bin/bash
# This file is part of Scanarium https://scanarium.com/ and licensed under the
# GNU Affero General Public License v3.0 (See LICENSE.md)
# SPDX-License-Identifier: AGPL-3.0-only

set -e
set -o pipefail

cd "$(dirname "$0")"
SCRIPT_DIR_ABS="$(pwd)"

cd ../..
ROOT_DIR_ABS="$(pwd)"

WARNINGS=0

error() {
    echo "ERROR:" "$@"
    exit 1
}

warn() {
    echo "WARNING:" "$@"
    WARNINGS=$((WARNINGS + 1))
}

for_each_keywords_file() {
    local FUNC="$1"
    shift
    for FILE_ABS in "$ROOT_DIR_ABS/scenes/"*"/actors/"*"/keywords/"*.txt
    do
        "$FUNC" "$FILE_ABS" "$@"
    done
}
