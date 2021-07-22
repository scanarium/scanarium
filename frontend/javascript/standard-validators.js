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

function standard_username_validator(node) {
  const username = node.value;
  if (!username.match(/^[a-z0-9][a-z0-9-]{2,37}[a-z0-9]$/)) {
    if (username.length < 4) {
      return localize('Too short (minimal length: {minimal_length})', {'minimal_length': '4'});
    }

    if (username[0] == '-') {
      return localize('Starting with "{start}" is not allowed', {'start': username[0]});
    }

    if (username[username.length - 1] == '-') {
      return localize('Ending with "{end}" is not allowed', {'end': username[username.length - 1]});
    }

    if (username.length > 39) {
      return localize('Too long (maximum length: {maximum_length})', {'maximum_length': '39'});
    }

    return localize('Only lowercase letters, digits and dashes are allowed');
  }
  return true;
}
