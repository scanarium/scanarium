// This file is part of Scanarium https://scanarium.com/ and licensed under the
// GNU Affero General Public License v3.0 (See LICENSE.md)
// SPDX-License-Identifier: AGPL-3.0-only

class SettingsPageAdministration extends NamedPage {
    constructor() {
        const name = localize_parameter('page_title', 'Administration');
        super('administration', name);
    }

    initContent() {
        this.initContentUi();
        this.initContentDeveloperModeUi();
        this.initContentActorReset();
        this.initContentPasswortSwitch();
    }

    initContentUi() {
        var that = this;
        this.appendSectionHeader('User interface');

        const uiFollowScannedActorSceneParameter = 'followScannedActorScene';
        var uiFollowScannedActorScene;

        var form = new ManagedForm('ui-settings', false);
        this.uiForm = form;

        uiFollowScannedActorScene = form.addCheckbox(
            localize('Switch scene'),
            'scanning-actor-switches-scene',
            undefined,
            localize('when an actor of a different scene got scanned'),
            getUrlParameterBoolean(uiFollowScannedActorSceneParameter ,true));
        uiFollowScannedActorScene.onChangedAndValid = function(event) {
            setUrlParameter(uiFollowScannedActorSceneParameter, uiFollowScannedActorScene.checked);

            event.stopPropagation();
            event.preventDefault();
        };

        form.addFixedTextField(localize('Language'), 'ui-setting-language', localize('Loading localization data ...'));

        this.loadLocalizationsConfig();

        this.appendElement(form.getElement());
    }

    initContentDeveloperModeUi() {
        var that = this;
        this.developerModeHeader = this.appendSectionHeader('Developer Mode');
        this.developerModeHeader.classList.add('hidden');

        var form = new ManagedForm('developer-mode-settings', false);
        this.developerModeForm = form.getElement();
        this.developerModeForm.classList.add('hidden');

        this.developerModeShowFrameCounter = form.addCheckbox(
            localize('Show frame counter'),
            'developer-mode-show-frame-counter',
            undefined,
            '',
            FrameCounter.isVisible());
        this.developerModeShowFrameCounter.onChangedAndValid = function(event) {
            FrameCounter.setVisibility(that.developerModeShowFrameCounter.checked);
            event.stopPropagation();
            event.preventDefault();
        };

        this.developerModeShowDeveloperInformation = form.addCheckbox(
            localize('Show developer information'),
            'developer-mode-show-developer-information',
            undefined,
            '',
            DeveloperInformation.isVisible());
        this.developerModeShowDeveloperInformation.onChangedAndValid = function(event) {
            DeveloperInformation.setVisibility(that.developerModeShowDeveloperInformation.checked);
            event.stopPropagation();
            event.preventDefault();
        };

        this.appendElement(form.getElement());
    }

    createResetButton(cgi, scene, label, warning) {
        var button = document.createElement('button');
        button.textContent = label;
        button.style['font-size'] = SettingsButton.button.style['font-size'];
        button.onclick = function(e) {
            if (confirm(warning)) {
                var data = new FormData();
                data.append('scene', scene);
                callCgi(cgi, data);
            }
            e.stopPropagation();
            e.preventDefault();
        };

        var wrapper = document.createElement('p');
        wrapper.appendChild(button);
        return wrapper;
    }

    initContentActorReset() {
        const cgi = 'reset-dynamic-content';
        if (!isCgiForbidden(cgi)) {
            this.appendSectionHeader('Delete actors');

            var resetButton;
            resetButton = this.createResetButton(
                cgi, scene,
                localize('Reset scene "{scene_name}"', {'scene_name': scene}),
                localize('Really reset the scene "{scene_name}", delete this scenes\' scanned actors, and start afresh? (This cannot be undone)', {'scene_name': scene})
            );
            this.appendElement(resetButton);

            resetButton = this.createResetButton(
                cgi, '',
                localize('Reset all scenes'),
                localize('Really reset all scenes, delete all scanned actors, and start afresh? (This cannot be undone)')
            );
            this.appendElement(resetButton);
        }
    }

    initContentPasswortSwitch() {
        const cgi = 'update-password';
        if (!isCgiForbidden(cgi)) {
            this.appendSectionHeader('Change password');

            var oldPasswordInput;
            var newPasswordInput;
            var confirmPasswordInput;
            var form;
            var submit = function(event) {
                var data = new FormData();
                data.append('old-password', oldPasswordInput.value);
                data.append('new-password', newPasswordInput.value);
                callCgi(cgi, data, (is_ok) => {
                    if (is_ok) {
                        oldPasswordInput.value = '';
                        newPasswordInput.value = '';
                        confirmPasswordInput.value = '';
                        form.validate();
                    }
                });

                event.stopPropagation();
                event.preventDefault();
                PauseManager.resume();
            }
            form = new ManagedForm('update-password-form', submit, localize('Change password'));

            var old_password_validator = function(node) {
                const password = node.value;

                if (password.length == '') {
                    return localize('This field may not be empty');
                }

                return true;
            }

            var new_password_validator = function(node) {
                const password = node.value;

                var result = standard_password_validator(node);
                if (result !== true) {
                    return result;
                }

                if (document.getElementById('new-password').value != document.getElementById('confirm-password').value) {
                    return localize('New password and its confirmation do not match');
                }
                return true;
            }

            oldPasswordInput = form.addPassword(localize('Current password'), 'current-password', standard_not_empty_validator);
            newPasswordInput = form.addPassword(localize('New password'), 'new-password', new_password_validator);
            confirmPasswordInput = form.addPassword(localize('Confirm new password'), 'confirm-password', new_password_validator);

            this.appendElement(form.getElement());
        }
    }

    loadLocalizationsConfig() {
        var self = this;
        if (Object.keys(localizations_config).length == 0) {
            loadDynamicConfig('localization/localizations.json', function(payload) {
                localizations_config = sanitize_dictionary(payload, undefined, true);
                self.loadedLocalizationsConfig();
            });
        } else {
            self.loadedLocalizationsConfig();
        }
    }

    loadedLocalizationsConfig() {
        var languageDropDown = this.uiForm.addDropDown(undefined, 'ui-setting-language', undefined, 'bari');

        localizations_config['localizations'].sort().forEach(key => {
            const selected = (key == language);
            var l10n_in_same_l10n = localizations_config[key + '-' + key] || key;
            var l10n_localized = localize_parameter('language', key);
            var text = key;
            if (l10n_in_same_l10n != key) {
                text += ' - ' + l10n_in_same_l10n;
                if (l10n_localized != key && l10n_localized != l10n_in_same_l10n) {
                    text += ' (' + l10n_localized + ')';
                }
            }

            languageDropDown.addOption(text, key, selected);
        });
        languageDropDown.onChangedAndValid = function(event) {
            if (languageDropDown.selectedOptions.length > 0) {
                const selected = languageDropDown.selectedOptions[0].value;
                setUrlParameter('language', selected, selected != language);
            }

            event.stopPropagation();
            event.preventDefault();
        };
    }

    onShowPage() {
        if (DeveloperMode.enabled) {
            this.developerModeHeader.classList.remove('hidden');
            this.developerModeForm.classList.remove('hidden');

            if (this.developerModeShowFrameCounter) {
                this.developerModeShowFrameCounter.setChecked(FrameCounter.isVisible());
            }
            if (this.developerModeShowDeveloperInformation) {
                this.developerModeShowDeveloperInformation.setChecked(DeveloperInformation.isVisible());
            }
        }
    }
}
