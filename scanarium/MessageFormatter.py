# This file is part of Scanarium https://scanarium.com/ and licensed under the
# GNU Affero General Public License v3.0 (See LICENSE.md)
# SPDX-License-Identifier: AGPL-3.0-only

import logging

logger = logging.getLogger(__name__)


class MessageFormatter(object):
    def __init__(self, config=None):
        super(MessageFormatter, self).__init__()
        self._config = config

    def capitalize_first(self, string):
        if string:
            # This is different from str.capitalize, as it does not lower-case
            # the 2nd character onwards.
            string = string[0].upper() + string[1:]
        return string

    def format_message(self, template, parameters):
        split = template.split('{')
        for idx in range(1, len(split)):
            try:
                conversion = None
                (param_name, rest) = split[idx].split('}', 1)
                if '!' in param_name:
                    (param_name, conversion) = param_name.rsplit('!', 1)
                    if conversion == 'S':
                        conversion = self.capitalize_first
                    elif conversion == '':
                        conversion = None
                    else:
                        raise RuntimeError(
                            f'Unknown conversion "{conversion}"')

                if param_name.startswith('conf:placeholders.'):
                    # As we only need to inject for the `placeholders` group
                    # for now, we artifictially restrict it to `placeholders`
                    # to avoid accidentally allowing exfiltration of maybe
                    # sensitive configuration settings (passwords?). We
                    # currently do not have sensitive information in our config
                    # files, and users cannot trigger backend translation of
                    # arbitrary keys, but we're extra defensive here. We might
                    # open that up later if needed. (The code below works for
                    # arbitrary groups)

                    # As `self._config` may be None, the below
                    # `self._config.get(...)` might throw an exception. But the
                    # outer try/except block does the right thing.
                    key, subkey = param_name[5:].split('.', 1)
                    param_value = self._config.get(
                        key, subkey, allow_empty=True, allow_missing=True,
                        default='')
                else:
                    param_value = parameters[param_name]

                if conversion:
                    param_value = conversion(param_value)

                split[idx] = str(param_value) + rest
            except Exception:
                split[idx] = '{' + split[idx]

        return ''.join(split)
