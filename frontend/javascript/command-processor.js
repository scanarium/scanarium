// This file is part of Scanarium https://scanarium.com/ and licensed under the
// GNU Affero General Public License v3.0 (See LICENSE.md)
// SPDX-License-Identifier: AGPL-3.0-only

var CommandProcessor = {
    recentUuids: [null, null, null, null, null, null, null, null, null, null],
    lastFullyProcessedUuid: null,

    isNew: function(uuid) {
        return (uuid == null || uuid == '' || !(this.recentUuids.includes(uuid)));
    },

    markOld: function(uuid) {
        this.recentUuids.shift();
        this.recentUuids.push(uuid);
    },

    processCommandActor: function(capsule, replay) {
        var is_ok = sanitize_boolean(capsule, 'is_ok');
        var command = sanitize_string(capsule, 'command');
        var parameters = sanitize_list(capsule, 'parameters');
        var uuid = sanitize_string(capsule, 'uuid');

        var template;
        if (is_ok) {
            template = 'Added new {actor_name}';
            if (command == scene) {
                var flavor = sanitize_string(capsule.payload, 'flavor')
                if (typeof actorManager !== 'undefined') {
                    // We add the actor, even if `replay` is true, as
                    // this will help showing a recently scanned actor
                    // more quickly. But we mark them as `isNewScan` only
                    // when not replaying.
                    actorManager.loadCreateAndAddActor(parameters[0], flavor, {
                      isNewScan: !replay,
                    });
                }
            }
            if (PageInsertionHint != null && getConfig('drop_page_insertion_hint_after_scan')) {
                if (!replay) {
                    PageInsertionHint.setInvisible();
                }
            }

            if (command != scene && !replay && getUrlParameterBoolean('followScannedActorScene', true)) {
                setUrlParameter('scene', command, true, uuid);
            }
        } else {
            if (sanitize_string(capsule, 'error_message') || sanitize_string(capsule, 'error_template')) {
                // There is a proper error message, so we use that.
                template = false;
            } else {
                // There is no proper error message, so we provide the best we can
                template = 'Failed to scan new actor drawing for {actor_name}';
            }
        }
        if (template && command != scene) {
            template += ' for scene {scene_name}';
        }
        return template ? localize(template, {
            'actor_name': parameters[0],
            'scene_name': command,
        }) : template;
    },

    processCommandDebug: function(capsule, replay) {
        var is_ok = sanitize_boolean(capsule, 'is_ok');
        var parameters = sanitize_list(capsule, 'parameters');
        var template = 'Unknown debug command received';
        if (parameters.length > 0) {
          if (['ok', 'fail'].includes(parameters[0])) {
            template = false;
          } else if (parameters[0] == 'toggleFps') {
            if (is_ok) {
              if (!replay) {
                  FrameCounter.toggleVisibility();
              }
              template = 'Toggled frames-per-second counter';
            } else {
              template = 'Toggling frames-per-second counter failed';
            }
          } else if (parameters[0] == 'toggleDevInfo') {
            if (is_ok) {
              if (!replay) {
                  DeveloperInformation.toggleVisibility();
              }
              template = 'Toggled developer information';
            } else {
              template = 'Toggling developer information failed';
            }
          }
        }
        return template ? localize(template) : false;
    },

    processCommandSwitchScene: function(capsule, replay) {
        var uuid = sanitize_string(capsule, 'uuid');
        var is_ok = sanitize_boolean(capsule, 'is_ok');
        var parameters = sanitize_list(capsule, 'parameters');
        if (is_ok) {
            template = 'Switching to scene {scene_name}';
            if (!replay) {
                setUrlParameter('scene', parameters[0], true, uuid);
            }
        } else {
            template = 'Cannot switch to scene {scene_name}';
        }
        return localize(template, {
            'scene_name': parameters[0],
        });
    },

    processCommandSystem: function(capsule, replay) {
        var is_ok = sanitize_boolean(capsule, 'is_ok');
        var parameters = sanitize_list(capsule, 'parameters');
        var template = 'Unknown system command received';
        if (parameters.length > 0) {
          if (parameters[0] == 'poweroff') {
            if (is_ok) {
              template = 'Shutdown initiated';
            } else {
              template = 'Shutdown initiation failed';
            }
          }
        }
        return localize(template);
    },

    processCommandReset: function(capsule, replay) {
        var uuid = sanitize_string(capsule, 'uuid');
        var is_ok = sanitize_boolean(capsule, 'is_ok');
        var parameters = sanitize_list(capsule, 'parameters');
        var reset_scene = '';
        if (parameters.length >= 2) {
            reset_scene = parameters[1];
        }
        if (is_ok && parameters.length == 2 && parameters[0] == 'DynamicContent') {
            if (reset_scene == '') {
                template = 'All scenes got reset';
            } else {
                template = 'Scene \"{scene_name}\" got reset';
            }

            if (reset_scene == '' || reset_scene == scene) {
                // The current scene got reset, so we need to reload.
                // Unless `replay` is true, because then we've reloaded already.
                if (!replay) {
                    updateLocation(localize('Automatic page reload required to finish resetting the scene.'), undefined, undefined, uuid);
                }
            }
        } else {
            if (reset_scene == '') {
                template = 'Resetting all scenes failed';
            } else {
                template = 'Resetting scene \"{scene_name}\" failed';
            }
        }
        return localize(template, {'scene_name': reset_scene});
    },

    processNew: function(capsule, replay) {
        var is_ok = sanitize_boolean(capsule, 'is_ok');
        var command = sanitize_string(capsule, 'command');
        var parameters = sanitize_list(capsule, 'parameters');
        var msg;
        if ('command' in capsule && capsule['command'] != null) {
            if (command == 'debug') {
                msg = this.processCommandDebug(capsule, replay);
            } else if (command == 'reset') {
                msg = this.processCommandReset(capsule, replay);
            } else if (command == 'switchScene') {
                msg = this.processCommandSwitchScene(capsule, replay);
            } else if (command == 'system') {
                msg = this.processCommandSystem(capsule, replay);
            } else {
                msg = this.processCommandActor(capsule, replay);
            }

            if (!msg && msg !== false) {
                msg = localize('{command_name} command ' + (is_ok ? 'ok' : 'failed'),
                               {'command_name': command});
            }
        }

        if (!msg) {
                msg = '';
        }

        var uuid = sanitize_string(capsule, 'uuid');
        if (uuid) {
            setUrlParameter('lastFullyProcessedUuid', uuid)
        }

        var error_message = sanitize_string(capsule, 'error_message');
        var error_template = sanitize_string(capsule, 'error_template');
        var error_parameters = sanitize_dictionary(capsule, 'error_parameters');
        error_template = error_template || error_message;
        if (error_template) {
            if (msg) {
                msg += ': ';
            }
            msg += localize(error_template, error_parameters);
        }

        const method = sanitize_string(capsule, 'method');
        if (method && (getConfig('prefix-messages-with-method') || !msg)) {
            const is_ok_text = (is_ok ? 'ok' : 'failed')
            const prefix = localize('{method_name} ' + is_ok_text, {'method_name': method});
            msg = prefix + (msg ? (': ' + msg) : '');
        }
        message = MessageManager.addMessage(msg, is_ok ? 'ok' : 'failed', undefined, uuid);
        if (getConfig("documentation_url")) {
            const error_code = sanitize_string(capsule, 'error_code');
            if (error_code && getConfig('documentation_anchored_error_codes').includes(error_code)) {
                MessageManager.addButtonToMessage(message, localize('Online Help'), () => {
                    var target = getConfig("documentation_url")
                    target += '#error-code-' + error_code;
                    const reason = localize(
                        'Forwarding to {url-description}.',
                        {'url-description': 'online help'})
                    updateLocation(reason, target);
                });
            }
        }
        return message;
    },

    /* If `replay` is true, the command is processed as usual, and messages get
       added, but no actions (changing urls, messing with url parameters, ...)
       are taken. Only recently scanned actors are added regardless
    */
    process: function(capsule, replay) {
        var ret = null;
        var uuid = sanitize_string(capsule, 'uuid');
        if (this.isNew(uuid) || replay) {
            this.markOld(uuid);
            ret = this.processNew(capsule, replay);
        }
        return ret;
    }
};

