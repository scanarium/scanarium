// This file is part of Scanarium https://scanarium.com/ and licensed under the
// GNU Affero General Public License v3.0 (See LICENSE.md)
// SPDX-License-Identifier: AGPL-3.0-only

class ManagedForm {
    /* submit_action: Either a function, false or a falsy value.
         If it's a function, the function will get called upon submit and
           default form behaviour (changing url etc) is not suppressed.
         If false, the default form behaviour is suppressed, and submitting the
           form does nothing.
         If a different falsy value, the default form behaviour is not
           suppressed.
     */
    constructor(id, submit_action, submit_button_caption) {
        var self = this;
        var form = document.createElement('form');
        var button;
        var font_size = Math.ceil(16 * window.devicePixelRatio).toString() + 'px';

        form.id = id;
        form.novalidate = true; // lowercase V according to MDN
        form.noValidate = true; // uppercase V is used in Firefox
        form.onsubmit = function(event) {
            self._onsubmit(event);
        }
        if (submit_button_caption) {
            button = document.createElement('button');
            button.id = form.id + '-submit-button';
            button.textContent = submit_button_caption;
            button.style['font-size'] = font_size;

            form.appendChild(button);
        }
        this.form = form;
        this.submit_action = submit_action;
        this.submit_button = button;
        this.font_size = font_size;
        this.validate();
    }

    _getFirstId(control) {
        var ret = control.id;
        control.childNodes.forEach(child => {
            if (!ret) {
                ret = this._getFirstId(child);
            }
        });
        return ret;
    }

    addControl(caption, control, validation) {
        var self = this;

        var controlId = this._getFirstId(control);

        var oldRow = null;
        this.form.childNodes.forEach(child => {
            if (!oldRow && child.id == 'form-row-' + controlId) {
                oldRow = child;
            }
        });

        if (!caption && oldRow && oldRow.hasChildNodes() && oldRow.firstChild.nodeName.toUpperCase() == 'LABEL') {
            caption = oldRow.firstChild.textContent;
        }

        var label = document.createElement('label');
        label.for = controlId;
        label.textContent = caption;

        if (validation) {
            control.scValidation = validation;
        }

        var validationContainer = document.createElement('div');
        validationContainer.id = controlId + '-validation-message';
        validationContainer.className = 'validation-message';

        control.oninput = function(event) {
            control.hasSeenInteraction = true;

            self.validate();

            if (!validationContainer.hasChildNodes() && control.onChangedAndValid) {
                control.onChangedAndValid(event);
            }
        }
        control.onchange = control.oninput;

        var row = document.createElement('div');
        row.className = 'form-row';
        row.id = 'form-row-' + controlId;

        row.appendChild(label);
        row.appendChild(control);
        row.appendChild(validationContainer);
        if (oldRow) {
            this.form.replaceChild(row, oldRow);
        } else if (this.submit_button) {
            this.form.insertBefore(row, this.submit_button);
        } else {
            this.form.appendChild(row);
        }
        control.rowElement = row;
        this.validate();
    }

    initStandardControl(control, id, explanation, caption) {
        control.id = id;
        control.name = id;
        control.placeholder = (typeof(explanation) !== 'undefined' ? explanation : caption);
        control.required = true;
        control.style['font-size'] = this.font_size;
    }

    addInput(caption, id, validation, type, explanation) {
        var input = document.createElement('input');
        input.type = type ? type : 'text';
        this.initStandardControl(input, id, explanation, caption);
        this.addControl(caption, input, validation);

        return input;
    }

    addPassword(caption, id, validation, explanation) {
        return this.addInput(caption, id, validation, 'password', explanation);
    }

    addEmail(caption, id, validation, explanation) {
        return this.addInput(caption, id, validation, 'email', explanation);
    }

    addTextArea(caption, id, validation, explanation) {
        var textarea = document.createElement('textarea');
        this.initStandardControl(textarea, id, explanation, caption);
        textarea.cols = 30;
        textarea.rows = 8;
        this.addControl(caption, textarea, validation);

        return textarea;
    }

    addCheckbox(caption, id, validation, explanation, initialValue) {
        var span = document.createElement('span');
        span.className = 'form-element';
        span.id = id + '-form-element';

        var input = document.createElement('input');
        input.type = 'checkbox';
        if (typeof initialValue !== 'undefined') {
            input.checked = initialValue;
        }
        this.initStandardControl(input, id, explanation, caption);
        Object.defineProperty(input, 'hasSeenInteraction', { get: function() {
            return span.hasSeenInteraction;
        }});
        input.setChecked = function(checked) {
            if (input.checked != checked) {
                input.checked = checked;

                var event = document.createEvent('Event');
                event.initEvent('change', true, true);
                input.dispatchEvent(event);
            }
        }
        input.toggle = function() {
            input.setChecked(!input.checked);
        }
        span.appendChild(input);
        span.onChangedAndValid = function(event) {
            if (input.onChangedAndValid) {
                input.onChangedAndValid(event);
            }
        }

        if (explanation) {
            var label = document.createElement('label');
            label.for = id;
            label.textContent = explanation;
            label.onclick = input.toggle;
            span.appendChild(label);
        }

        this.addControl(caption, span, validation);

        input.rowElement = span.rowElement;

        return input;
    }

    addFixedTextField(caption, id, text) {
        var span = document.createElement('span');
        span.id = id;
        span.className = 'form-fixed-text-element';
        span.textContent = text;

        this.addControl(caption, span);
        return span;
    }

    addDropDown(caption, id, validation, explanation) {
        var dropDown = document.createElement('select');
        this.initStandardControl(dropDown, id, explanation, caption);
        dropDown.addOption = function(text, value, selected) {
            dropDown.appendChild(new Option(text, value, selected, selected));
        };

        this.addControl(caption, dropDown, validation);

        return dropDown;
    }

    _validateNode(node, hideValidationMessages, root) {
        var result = true;

        if (!root) {
            root = node;
        }

        if (node.scValidation) {
            result = node.scValidation(node);

            // We cannot use `document.getElementById` here, as the form need
            // not be hooked into DOM at the time of validation.
            var validationContainer = root.querySelector('#' + node.id + '-validation-message');
            if (validationContainer) {
                validationContainer.textContent = '';
            }
            if (result === true) {
                if (node.setCustomValidity) {
                    node.setCustomValidity('');
                }
            } else {
                var message = localize('Invalid value');
                if (result !== false && result !== '' && result !== null) {
                    message = result;
                }

                if (hideValidationMessages) {
                    message = '';
                }

                if (node.setCustomValidity) {
                    node.setCustomValidity(message);
                }

                if (validationContainer) {
                    validationContainer.textContent = message;
                }

                result = false;
            }
        }

        node.childNodes.forEach(child => {
            const child_result = this._validateNode(child, hideValidationMessages, root);
            result &= child_result;
        });

        return result;
    }

    hasSeenInteraction() {
        var hasSeenInteraction = false;
        var elements = this.getElement().elements;
        for (var i=0; !hasSeenInteraction && i < elements.length; i++) {
            var element = elements[i];
            hasSeenInteraction = element.hasSeenInteraction;
        }
        return hasSeenInteraction;
    }

    validate() {
        var result = this._validateNode(this.getElement(), !this.hasSeenInteraction());
        if (this.submit_button) {
            this.submit_button.disabled = !result;
        }
        return result;
    }

    _onsubmit(event) {
        if (this.validate() && this.submit_action !== false) {
            if (this.submit_action) {
                this.submit_action(event);
            }
        } else {
            event.stopPropagation();
            event.preventDefault();
        }
    }

    getElement() {
        return this.form;
    }
}
