#!/bin/bash
# This file is part of Scanarium https://scanarium.com/ and licensed under the
# GNU Affero General Public License v3.0 (See LICENSE.md)
# SPDX-License-Identifier: AGPL-3.0-only

set -e
set -o pipefail

sort_file() {
    local FILE="$1"

    jq -S . <"$FILE" >"$FILE.tmp" && mv "$FILE.tmp" "$FILE"
}

for FILE in conf/qr-code-maps/*.json
do
    sort_file "$FILE"
done
