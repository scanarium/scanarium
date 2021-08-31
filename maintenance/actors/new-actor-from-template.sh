#!/bin/bash
# This file is part of Scanarium https://scanarium.com/ and licensed under the
# GNU Affero General Public License v3.0 (See LICENSE.md)
# SPDX-License-Identifier: AGPL-3.0-only

set -e
set -o pipefail

# Call as:
#
#  maintenance/actors/new-actor-from-template.sh scene/$SCENE/actors/$OLD_NAME $NEW_NAME
#

cd "$(dirname "$0")"
cd ../..

TEMPLATE="$1"
NEW_NAME="$2"

SCENE_DIR="scenes"
ACTORS_DIR="actors"

OLD_NAME="$(basename "$TEMPLATE")"
SCENE="$(basename "$(dirname "$(dirname "$TEMPLATE")")")"

FULL_TARGET_DIR="$SCENE_DIR/$SCENE/$ACTORS_DIR/$NEW_NAME"

DECORATION_VERSION="$(ls -1 conf/decoration-d-*.svg | sed -e 's@^.*/decoration-d-0*\([1-9][0-9]*\)\.svg@\1@' | sort -n | tail -n 1)"

update_qr_map() {
    NEXT_ID=$(($(grep '"[0-9][0-9]*":' conf/qr-code-maps/SCANARIUM.COM.json | sort | tail -n 1 | sed -e 's/^ *"0*\([1-9][0-9]*\)\":.*/\1/') + 1))
    NEXT_ID_FORMATTED=$(printf "%03d" "$NEXT_ID")
    sed -e 's/^\( *"001":.*\)/"'"$(printf "%03d" "$NEXT_ID")"'":"'"$SCENE:$NEW_NAME:d_$DECORATION_VERSION"'",\n\1/' -i conf/qr-code-maps/SCANARIUM.COM.json
    maintenance/qr-code-maps/sort.sh
}

create_actor_files() {
    mkdir -p "$FULL_TARGET_DIR"

    for VARIANT in \
        ".js" \
        "-undecorated-d-${DECORATION_VERSION}.svg" \

    do
        cp "$TEMPLATE/$OLD_NAME$VARIANT" "$FULL_TARGET_DIR/$NEW_NAME$VARIANT"
    done
    sed -e "s/$OLD_NAME/$NEW_NAME/g" -i "$FULL_TARGET_DIR/$NEW_NAME.js"
}

create_actor() {
    echo "$TEMPLATE -> $NEW_NAME"

    create_actor_files
    update_qr_map
}

create_actor

echo "pass"