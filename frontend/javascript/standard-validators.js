// This file is part of Scanarium https://scanarium.com/ and licensed under the
// GNU Affero General Public License v3.0 (See LICENSE.md)
// SPDX-License-Identifier: AGPL-3.0-only

// -- Standard checks --------------------------------------------------

function standard_check_not_empty(value) {
    if (!value) {
        return localize('Must not be empty');
    }

    return true;
}

function standard_check_minimal_length(value, minimal_length) {
    var result = standard_check_not_empty(value);
    if (result !== true) {
        return result;
    }

    if (value.length < minimal_length) {
        return localize('Too short (minimal length: {minimal_length})', {'minimal_length': String(minimal_length)});
    }
    return true;
}

function standard_check_maximal_length(value, maximal_length) {
    if (value.length > maximal_length) {
        return localize('Too long (maximum length: {maximum_length})', {'maximum_length': String(maximal_length)});
    }
    return true;
}

function standard_check_does_not_start_with(value, forbidden_start) {
    if (value && value[0] == forbidden_start) {
      return localize('Starting with "{start}" is not allowed', {'start': forbidden_start});
    }

    return true;
}

function standard_check_does_not_end_with(value, forbidden_end) {
    if (value && value[value.length - 1] == forbidden_end) {
      return localize('Ending with "{end}" is not allowed', {'end': forbidden_end});
    }

    return true;
}

function standard_check_does_not_contain(value, forbidden) {
    if (value && value.indexOf('--') != -1) {
      return localize('Must not contain "{forbidden}"', {'forbidden': forbidden});
    }

    return true;
}



// -- Standard validators ----------------------------------------------

function standard_not_empty_validator(node) {
    const value = node.value;

    return standard_check_not_empty(value);
}

function standard_password_validator(node) {
    const password = node.value;
    const minimum_password_length = 6;

    return standard_check_minimal_length(password, minimum_password_length)
}

function standard_username_validator(node) {
  const username = node.value;

  var result = standard_check_minimal_length(username, 4);

  if (result === true) {
      result = standard_check_maximal_length(username, 39);
  }

  if (result === true) {
      result = standard_check_does_not_start_with(username, '-');
  }

  if (result === true) {
      result = standard_check_does_not_end_with(username, '-');
  }

  if (result === true) {
      result = standard_check_does_not_contain(username, '--');
  }

  if (result === true && !username.match(/^[a-z0-9][a-z0-9-]{2,37}[a-z0-9]$/)) {
    result = localize('Only lowercase letters, digits and dashes are allowed');
  }

  return result;
}

function validateCheckboxChecked(node) {
  if (node.querySelector('input[type="checkbox"]').checked) {
    return true;
  }
  return localize('Needs to be checked');
}
