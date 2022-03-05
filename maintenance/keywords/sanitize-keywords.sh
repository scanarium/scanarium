#!/bin/bash
# This file is part of Scanarium https://scanarium.com/ and licensed under the
# GNU Affero General Public License v3.0 (See LICENSE.md)
# SPDX-License-Identifier: AGPL-3.0-only

source "$(dirname "$0")/common.inc"

sanitize_file() {
echo "$@"
    local FILE_ABS="$1"
    sed <"$FILE_ABS" \
        -e 's/^\s\+//' \
        -e 's/\s\+$//' \
        | \
        (grep -v '^$' || true) | \
        sort -u >"$FILE_ABS.tmp"
    mv "$FILE_ABS.tmp" "$FILE_ABS"
}

main() {
    for_each_keywords_file sanitize_file
}

main
