// This file is part of Scanarium https://scanarium.com/ and licensed under the
// GNU Affero General Public License v3.0 (See LICENSE.md)
// SPDX-License-Identifier: AGPL-3.0-only

function standard_not_empty_validator(node) {
    const password = node.value;

    if (password.length == '') {
        return localize('This field may not be empty');
    }

    return true;
}

function standard_password_validator(node) {
    const password = node.value;
    const minimum_password_length = 6;

    if (password.length < minimum_password_length) {
        return localize('Password is too short (minimum: {count} characters)', {count: minimum_password_length});
    }
    return true;
}
