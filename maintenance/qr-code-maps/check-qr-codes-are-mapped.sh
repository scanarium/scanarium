#!/bin/bash
# This file is part of Scanarium https://scanarium.com/ and licensed under the
# GNU Affero General Public License v3.0 (See LICENSE.md)
# SPDX-License-Identifier: AGPL-3.0-only

source "$(dirname "$0")/common.inc"

ERRORS=0

DECORATION_VERSION="$(ls -1 conf/decoration-d-*.svg | sed -e 's@^.*/decoration-d-0*\([1-9][0-9]*\)\.svg@\1@' | sort -n | tail -n 1)"

error() {
    echo "ERROR:" "$@" >&2
    ERRORS=$((ERRORS+1))
}

assert_qr_code_is_mapped() {
    local QR_CODE="$1"
    if ! grep --quiet '^ *"[0-9]\{3,3\}": "'"$QR_CODE"'",\?$' "conf/qr-code-maps/"*
    then
        error "QR code \"$QR_CODE\" looks unmapped"
    fi
}

list_qr_codes() {
    find \
        commands/* scenes/*/actors \
        -mindepth 1 -maxdepth 1 \
        ! -name 'extra-decoration-*.svg' \
        | sed \
          -e 's@^\(commands\|scenes\)/@@' \
          -e 's@actors/@@' \
          -e 's@/@:@' \
          -e 's@$@:d_'"${DECORATION_VERSION}"'@' \

}

assert_all_qr_codes_are_mapped() {
    for QR_CODE in $(list_qr_codes)
    do
        assert_qr_code_is_mapped "$QR_CODE"
    done
    if [ "$ERRORS" != "0" ]
    then
        exit 1
    fi
}

assert_all_qr_codes_are_mapped
