#!/bin/bash
# This file is part of Scanarium https://scanarium.com/ and licensed under the
# GNU Affero General Public License v3.0 (See LICENSE.md)
# SPDX-License-Identifier: AGPL-3.0-only

set -e
set -o pipefail

cd "$(dirname "$0")"
cd ../..

for MARKER_FILE in scenes/*/actors/*/hidden
do
    if [ -e "$MARKER_FILE" ]
    then
        SCENE="$(cut -f 2 -d / <<<"$MARKER_FILE")"
        ACTOR="$(cut -f 2 -d / <<<"$MARKER_FILE")"
        echo "Scene: $SCENE, Actor: $ACTOR, Marker file: $MARKER_FILE"
    else
        echo "No hidden actors found" >&2
    fi
done
