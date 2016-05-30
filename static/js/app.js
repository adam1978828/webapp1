String.prototype.supplant = function(o) {
    return this.replace(/{([^{}]*)}/g,
        function(a, b) {
            var r = o[b];
            return typeof r === 'string' || typeof r === 'number' ? r : a;
        }
    );
};

(function($, window, document, undefined) {

    $.fn.reverse = [].reverse;

    $.fn.serializeObject = function() {
        var o = {};
        var a = this.serializeArray();
        $.each(a, function() {
            if (o[this.name] !== undefined) {
                if (!o[this.name].push) {
                    o[this.name] = [o[this.name]];
                }
                o[this.name].push(this.value || '');
            } else {
                o[this.name] = this.value || '';
            }
        });
        return o;
    };

    $.fn.serializeNestedForms = function() {
        var res = $(this).serializeObject(),
            forms = $(this).find('form');
        $.each(forms, function() {
            var data = $(this).serializeObject(),
                name = this.getAttribute('name'),
                attrName = $(this).closest('[data-name]').attr('data-name');
            if (!res[attrName])
                res[attrName] = {};
            res[attrName][name] = data;
        });
        return res;
    };

    $.extend($$, {
        clientValidate: function() {
            $$.register('validation', {
                wrapper: $$.ready,
                func: function() {

                    // ! Validation

                    // - Validate
                    $('form.validate').not('.ready').each(function() {
                        $(this).validate({
                            submitHandler: function(form) {
                                // $(this).data('submit') ? $(this).data('submit')() : form.submit();
                            }
                        });
                    });

                    // - Reset validation on form reset
                    $('form.validate').on('reset', function() {
                        var $form = $(this);
                        $form.validate().resetForm();
                        $form.find('label.error').remove().end()
                            .find('.error-icon').remove().end()
                            .find('.valid-icon').remove().end()
                            .find('.valid').removeClass('valid').end()
                            .find('.customfile.error').removeClass('error');
                    }).addClass('ready');


                    // ! Polyfill: 'form' tag on <input>s
                    if (!('form' in document.createElement('input'))) {
                        $('input:submit').each(function() {
                            var $el = $(this);
                            if ($el.attr('form')) {
                                $el.click(function() {
                                    $('#' + $el.attr('form')).submit();
                                });
                            }
                        });
                        $('input:reset').each(function() {
                            var $el = $(this);
                            if ($el.attr('form')) {
                                $el.click(function() {
                                    $('#' + $el.attr('form'))[0].reset();
                                });
                            }
                        });
                    }
                },
                init: function() {
                    // - Add new method: password
                    $.validator.addMethod('strongpw', function(pwd, el) {
                        return $.pwdStrength(pwd) > mango.config.forms.pwdmeter.okayThreshold;
                    }, 'Your password is insecure');

                    // - Add new method: checked
                    $.validator.addMethod('checked', function(val, el) {
                        return !!$(el)[0].checked;
                    }, 'You have to select this option');

                    // - Set defaults
                    $.validator.setDefaults({

                        // Do not ignore chosen-selects | datepicker mirrors | checkboxes | radio buttons
                        ignore: ':hidden:not(select.chzn-done):not(input.mirror):not(:checkbox):not(:radio):not(.dualselects),.ignore',

                        // If a field is switches from invalid to valid
                        success: function(label) {
                            // Change icon from error to valid
                            $(label).prev().filter('.error-icon').removeClass('error-icon').addClass('valid-icon');

                            // If file input: remove 'error' from '.customfile'
                            $(label).prev('.customfile').removeClass('error');
                        },

                        // Where to place the error labels
                        errorPlacement: function($error, $element) {

                            if ($element.hasClass('customfile-input-hidden')) {

                                $error.insertAfter($element.parent().addClass('error'));

                                // Password meter || Textarea || Spinner || Inline Datepicker || Checkbox || Radiobutton: No icon
                            } else if ($element.is(':password.meter') || $element.is('textarea') || $element.is('.ui-spinner-input') || $element.is('input.mirror')) {

                                $error.insertAfter($element);

                                // Checkbox: No icon, after replacement
                            } else if ($element.is(':checkbox') || $element.is(':radio')) {

                                if ($element.is(':checkbox')) {
                                    $error.insertAfter($element.next().next());
                                } else {
                                    // Find last radion button
                                    $error.insertAfter($('[name=' + $element[0].name + ']').last().next().next());
                                }
                            } else if ($element.is('select.chzn-done') || $element.is('.dualselects')) {
                                $error.insertAfter($element.next());
                            } else {
                                $error.insertAfter($element);
                                var $icon = $('<div class="error-icon icon" />').insertAfter($element).position({
                                    my: 'right',
                                    at: 'right',
                                    of: $element,
                                    offset: '-5 0',
                                    overflow: 'none',
                                    using: function(pos) {
                                        // Figure out the right and bottom css properties
                                        var offsetWidth = $(this).offsetParent().outerWidth();
                                        var right = offsetWidth - pos.left - $(this).outerWidth();

                                        // Position the element so that right and bottom are set.
                                        $(this).css({
                                            left: '',
                                            right: right,
                                            top: pos.top
                                        });
                                    }
                                });

                            }
                        },

                        // Reposition error labels and hide unneeded labels
                        showErrors: function(map, list) {
                            var self = this;

                            this.defaultShowErrors();

                            list.forEach(function(err) {

                                var $element = $(err.element),
                                    $error = self.errorsFor(err.element);
                                if ($element.data('errorType') == 'inline' || $element.is('select') || $element.is('textarea') || $element.hasClass('customfile-input-hidden') || $element.is('input.mirror') || $element.is(':checkbox') || $element.is(':radio') || $element.is('.dualselect')) {
                                    var $of;
                                    if ($element.is('select')) {
                                        $of = $element.next();
                                    } else if ($element.is(':checkbox') || $element.is(':radio')) {
                                        if ($element.is(':checkbox')) {
                                            $of = $element.next();
                                        } else {
                                            $of = $('[name=' + $element[0].name + ']').last().next().next();
                                        }
                                        $error.css('display', 'block');
                                    } else if ($element.is('input.mirror')) {
                                        $of = $element.prev();
                                    } else {
                                        $of = $element;
                                    }

                                    $error.addClass('inline').position({
                                        my: 'left top',
                                        at: 'left bottom',
                                        of: $of,
                                        offset: '0 5',
                                        collision: 'none'
                                    });

                                    if (!($element.is(':checkbox') && $element.is(':radio'))) {
                                        $error.css('left', '');
                                    }

                                    // Default: Tooltip labels
                                } else {

                                    $error.position({
                                        my: 'right top',
                                        at: 'right bottom',
                                        of: $element,
                                        offset: '1 8',
                                        using: function(pos) {
                                            // Figure out the right and bottom css properties
                                            var offsetWidth = $(this).offsetParent().outerWidth();
                                            var right = offsetWidth - pos.left - $(this).outerWidth();

                                            // Position the element so that right and bottom are set.
                                            $(this).css({
                                                left: '',
                                                right: right,
                                                top: pos.top
                                            });
                                        }
                                    });

                                } // End if

                                // Switch icon from valid to error
                                $error.prev().filter('.valid-icon').removeClass('valid-icon').addClass('error-icon');

                                // Hide error labe on .noerror
                                if ($element.hasClass('noerror')) {
                                    $error.hide();
                                    $element.next('.icon').hide();
                                }
                            });

                            // Hide success labels
                            this.successList.forEach(function(el) {
                                self.errorsFor(el).hide();
                            });

                        }
                    });
                }
            });
        },
        showModalMessage: function(modal_type, modal_message, close_function){
            var modal = $("#dialog_modal");
            modal.attr('title', modal_type);
            $("#dialog_modal .error").text(modal_message);
            modal.dialog({
                autoOpen: false,
                modal: true,
                resizable: false,
                draggable: false,
                show: null,
                hide: null
            });

            var modal_btn = modal.find('button');

            if (close_function == null){
                modal_btn.click(function() {
                    $(this).parents('.ui-dialog-content').dialog('close');
                });
            } else {
                modal_btn.click(close_function);
            }

            modal.dialog("open");
        },
        displayServerValidationResults: function(data) {
            var errors = $(data.errors);
            var resetInputs = $("form input");
            resetInputs.removeClass('error');
            errors.each(function(idx, val) {
                var input = $('#' + val.field);
                if (input.parent().attr("class") == "customfile error") {
                    // if the client validation for input type="file" has already fired
                    input.parent().next().text(val.message)
                } else {
                    if (input.next().attr('class') == undefined) {
                        input.after('<div class="error-icon icon" style="right: 5.99998px; top: 33.5px;"></div>');
                        input.next().removeClass('valid-icon');
                        input.next().addClass('error-icon');
                    }
                    if (input.next().next().attr('class') == undefined) {
                        input.next().after('<label class="error inline" for="' + val.field + '" style="top: -15px;">' + val.message + '</label>');
                    } else {
                        input.next().next().text(val.message);
                    }
                    input.next().next().show();
                    input.next().next().addClass('inline');
                    input.next().next().css({
                        'top': '-15px'
                    });
                }
            });
            setTimeout(function() {
                $('.error-icon, .error.inline').hide(500, function() {
                    $(this).removeClass('inline');
                });
            }, 30000);
        }
    });

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!(/^(GET|HEAD|OPTIONS|TRACE)$/.test(settings.type)) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", $.cookie('csrftoken'));
            }
        }
    });
})(jQuery, this, document);

$(document).ready(function() {
    var dialogForm = $("#dialog_form");
    var uiDialogTitle = $(".ui-dialog-title");

    // helper functions lie here
    var daysInMonth = function(month, year) {
        return new Date(year, month, 0).getDate();
    },
        range = function(x, from) {
            if (typeof(from) === 'undefined') from = 0;
            return Array.apply(null, Array(x)).map(function(_, i) {
                return from + i
            })
        },
        setDateSelector = function(dateSelector, day, month, year) {
            function setOptions(select, options, selected) {
                var isYear = select.getAttribute('data-id') == 'year',
                    optVal = isYear ? 1 : 0;
                select.options.length = optVal;
                for (var i = optVal, len = options.length + optVal; i < len; i++) {
                    select.options[i] = (options[i - optVal] == selected) ?
                        new Option(options[i - optVal], isYear ? options[i - optVal] : i + 1, false, true) :
                        new Option(options[i - optVal], isYear ? options[i - optVal] : i + 1);
                }
                $(select).trigger('chosen:updated')
            }

            var daySelect = dateSelector.querySelector('[data-id="day"]'),
                monthSelect = dateSelector.querySelector('[data-id="month"]'),
                yearSelect = dateSelector.querySelector('[data-id="year"]');
            if (typeof(day) !== 'undefined') setOptions(daySelect, range(daysInMonth(month + 1, year), 1), day);
            if (typeof(month) !== 'undefined') setOptions(monthSelect, monthNames, monthNames[month]);
            if (typeof(year) !== 'undefined') setOptions(yearSelect, range(10, new Date().getFullYear()), year);
        },
        createDateSelector = function() {
            var dateSelector = document.createElement('div'),
                daySelect = document.createElement('select'),
                monthSelect = document.createElement('select'),
                yearSelect = document.createElement('select'),
                yearlyOption = new Option('Yearly', '0');
            dateSelector.setAttribute('data-id', 'skipPeriod');
            dateSelector.setAttribute('class', 'selectPeriod');
            daySelect.setAttribute('data-id', 'day');
            daySelect.setAttribute('name', 'day');
            monthSelect.setAttribute('data-id', 'month');
            monthSelect.setAttribute('name', 'month');
            yearSelect.setAttribute('data-id', 'year');
            yearSelect.setAttribute('name', 'year');
            yearSelect.options[0] = yearlyOption;
            dateSelector.appendChild(daySelect);
            dateSelector.appendChild(monthSelect);
            dateSelector.appendChild(yearSelect);
            setDateSelector(dateSelector, day.getDate(), day.getMonth(), day.getFullYear())
            $(daySelect).chosen({
                disable_search: true
            });
            $(monthSelect).chosen({
                disable_search: true
            });
            $(yearSelect).chosen({
                disable_search: true
            });
            $(yearSelect).live('change', function() {
                setDateSelector(this.parentNode, parseInt(daySelect.value), monthSelect.value - 1, parseInt(this.value))
            });
            $(monthSelect).live('change', function() {
                setDateSelector(this.parentNode, parseInt(daySelect.value), this.value - 1, parseInt(yearSelect.value))
            });
            return dateSelector;
        },
        chosenSearchResult = function(arr_index, value, disabled) {
            var searchResult = document.createElement('li');
            searchResult.setAttribute('class', 'active-result');
            searchResult.setAttribute('data-option-array-index', arr_index);
            searchResult.innerHTML = value;
            if (disabled)
                searchResult.setAttribute('disabled', true);
            return searchResult;
        },
        addNotification = function(data) {
            var history = document.querySelector('#activityHistoryBox'),
                item = document.createElement('div'),
                icon = document.createElement('icon'),
                startAlert = history.querySelector('#startNote'),
                message = document.createTextNode(data.message);
            $(startAlert).fadeOut('slow')
            item.setAttribute('class', 'alert ' + data.type);
            icon.setAttribute('class', 'icon');
            item.appendChild(icon);
            item.appendChild(message);
            //console.log(item)
            history.insertBefore(item, history.firstChild);
        },
        addDisk = function(event) {
            event.preventDefault();
            var url = $('#addDisc').attr('action');
            var f_company_id = $('#f_company_id').val();
            var upc = $('#upcLink').val();
            var rfId = $('#rfId').val();
            $.ajax({
                type: "POST",
                url: url,
                data: {
                    'f_company_id': f_company_id,
                    'upcLink': upc,
                    'rfId': rfId
                },
                dataType: "json",
                success: function(data) {
                    var inputRfId = $("#rfId")
                    addNotification(data);
                    if (data.type == "success") {
                        inputRfId.val('')
                        inputRfId.removeClass('valid')
                        inputRfId.focus()
                        $('#addDisc').find('label.error').remove().end()
                            .find('.error-icon').remove().end()
                            .find('.valid-icon').remove().end()
                            .find('.valid').removeClass('valid').end()
                            .find('.customfile.error').removeClass('error');
                    } else if (data.type == "error") {
                        $$.displayServerValidationResults(data)
                        inputRfId.select()
                    } else if (data.type == "warning") {
                        if (data.data.modal_html) {
                            var upcTransfer = $('#upcTransfer');
                            upcTransfer.html(data.data.modal_html);
                            upcTransfer.dialog('open');
                        }
                        inputRfId.select()
                    }
                }
            });
        },
        reassignDisk = function(e) {
            e.preventDefault();
            var vals = $('#addDisc').serializeObject(),
                urlPattern = $('#upcTransfer').attr('data-reassign-url'),
                reassignUrl = urlPattern.replace('0', vals.upcLink).replace('Dsk', vals.rfId);
            $.ajax({
                type: "POST",
                url: reassignUrl,
                data: vals,
                success: function(data) {
                    addNotification(data);
                    var upcTransfer = $('#upcTransfer');
                    upcTransfer.dialog('close');
                    var inputRfId = $('#rfId');
                    inputRfId.val('');
                    inputRfId.removeClass('valid');
                    inputRfId.focus();
                    var addDisc = $('#addDisc');
                    addDisc.find('label.error').remove().end()
                        .find('.error-icon').remove().end()
                        .find('.valid-icon').remove().end()
                        .find('.valid').removeClass('valid').end()
                        .find('.customfile.error').removeClass('error');
                },
                error: function() {
                    alert("FAIL! Cannot reassign UPC");
                }
            });
        },
        addMovieTranslation = function(lang_name, lang_id) {
            var transForm = $($('#transPattern').clone());
            transForm.removeAttr('id');
            transForm.find('.lang-name').html(lang_name);
            transForm.find('input[name="id"]').val(lang_id);
            $('#movieTranslations').append(transForm);

            /*
                Hope that person which wrote the code below
                is the most lazy person in the whole world
            */

            /*
            var translations = document.getElementById('movieTranslations'),
                translation = document.createElement('div'),
                header = document.createElement('div'),
                lang = document.createTextNode(lang_name),
                id = document.createElement('input'),
                content = document.createElement('form'),
                fields = document.createElement('fieldset'),
                rowTitle = document.createElement('div'),
                titleLabel = document.createElement('label'),
                title = document.createElement('div'),
                titleInput = document.createElement('input'),
                rowDesc = document.createElement('div'),
                descLabel = document.createElement('label'),
                desc = document.createElement('div'),
                descInput = document.createElement('textarea'),
                closeButton = document.createElement('span'),
                closeIcon = document.createTextNode('x');
            translation.setAttribute('class', 'pricing grid_6');
            translation.setAttribute('name', lang_name);
            header.setAttribute('class', 'title');
            closeButton.setAttribute('class', 'discard-translation')
            closeButton.appendChild(closeIcon);
            $(closeButton).on('click', function(e) {
                e.preventDefault();
                translations.removeChild(translation);
                //console.log(lang_name);
                var option = $('option[data-name="' + lang_name + '"]');
                option.removeAttr('disabled');
                $('#movieTranslation').trigger('chosen:updated');
            });
            header.appendChild(lang);
            header.appendChild(closeButton);
            content.setAttribute('class', 'validate full content');
            id.setAttribute('type', 'hidden');
            id.setAttribute('name', 'id');
            id.value = lang_id;
            fields.appendChild(id);
            rowTitle.setAttribute('class', 'row');
            titleLabel.setAttribute('for', 'title');
            titleLabel.innerHTML = "<strong> Title </strong > ";
            titleInput.setAttribute('name', 'title');
            titleInput.setAttribute('type', 'text');
            titleInput.setAttribute('class', 'required')
            titleInput.setAttribute('data-id', 'title');
            rowDesc.setAttribute('class', 'row');
            descLabel.setAttribute('for', 'description');
            descLabel.innerHTML = "<strong> Description </strong>";
            descInput.setAttribute('name', 'description');
            descInput.setAttribute('data-id', 'description');
            translation.appendChild(header);
            rowTitle.appendChild(titleLabel);
            title.appendChild(titleInput);
            rowTitle.appendChild(title);
            fields.appendChild(rowTitle);
            rowDesc.appendChild(descLabel);
            desc.appendChild(descInput);
            rowDesc.appendChild(desc);
            fields.appendChild(rowDesc);
            content.appendChild(fields);
            $(content).validate().resetForm();
            translation.appendChild(content);
            translations.appendChild(translation);
            */
            $$.utils.forms.resize();
        },
        // this must be in utils.js or so
        rand_pass = function(length) {
            var s = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
            var pass = '';
            for (i = 0; i < length; i++) {
                pass += s[Math.floor((Math.random() * s.length))];
            }
            return pass
        };
    //////////////////////////////////////////////////////////////////////////////////////
    /* new UI elements */
    $('input.inline-edit').each(function() {
        if (this.value.length != 0)
            this.style.width = this.value.length * 6 + 'px';
        else
            this.style.width = '56px';
    })
    //////////////////////////////////////////////////////////////////////////////////////
    $.each($('input[type="time"]'), function() {
        $(this).prop('value', this.getAttribute('data-time'))
    });

    // this should be in profile script
    $('#genProfilePassword').click(function(e) {
        $(e.target).siblings('input').val(rand_pass(8))
    });

    // prevent to submit forms by enter
    $('#f_create_kiosk, #f_create_company').keydown(function(event) {
        if (event.target.tagName == "INPUT" && event.keyCode == 13) {
            event.preventDefault();
            return false;
        }
    });

    if ($('#choosepayment').val() != "") {
        $('#choosepayment option:first-child').attr('selected', '');
        $('#pattern').children().hide();
    }
    $('#choosepayment').change(function() {
        var paymentid = $(this).val();
        var paymentajax = $(this).attr('data-action');
        if (paymentid != "") {
            $.ajax({
                type: "POST",
                url: paymentajax,
                data: {
                    data: paymentid
                },
                dataType: "html",
                success: function(data) {
                    $('#pattern').html(data);
                }
            });
        }
    });
    dialogForm.attr("title", "Add kiosk plan");
    dialogForm.dialog({
        autoOpen: false,
        modal: true,
        width: 400,
        resizable: false,
        draggable: false,
        open: function() {
            $(this).parent().css('overflow', 'visible');
            $$.utils.forms.resize();
        }
    }).find('button.cancel').live('click', function() {
        var $el = $(this).parents('.ui-dialog-content');
        $el.find('form')[0].reset();
        $el.dialog('close');
    });

    $('#addPricePlans, #editPricePlans').next().find('button[data-id="changePricePlan"]').live('click', function(event) {
        if ($('#addPricePlans, #editPricePlans').find('.error-icon').length == 0) {
            var inputs = $("form input");
            inputs.each(function(idx, val) {
                $(val).removeClass('error');
            });
            var $el = $(this).parents('form');
            var urlSavePricePlan = $('#addPricePlans, #editPricePlans').attr('action');
            var dataPricePlan = $('#addPricePlans, #editPricePlans').serializeObject();
            var dataObject = {};
            dataObject.priceField = dataPricePlan;
            $.ajax({
                type: "POST",
                url: urlSavePricePlan,
                data: {
                    mode: "save",
                    data: JSON.stringify(dataObject)
                },
                success: function(data) {
                    if (data.type == "error") {
                        var errors = $(data.errors);
                        var resetInputs = $("form input");
                        errors.each(function(idx, val) {
                            var input = $('#' + val.field);
                            if (input.next().attr('class') == undefined) {
                                input.after('<div class="error-icon icon" style="right: 5.99998px; top: 33.5px;"></div>');
                            }
                            if (input.next().next().attr('class') == undefined) {
                                input.next().after('<label class="error inline" for="' + val.field + '" style="top: -15px;">' + val.message + '</label>');
                            } else {
                                input.next().next().text(val.message);
                            }
                            input.next().next().show();
                            input.next().next().addClass('inline');
                            input.next().next().css({
                                'top': '-15px'
                            });
                            input.next().removeClass('valid-icon');
                            input.next().addClass('error-icon');
                        });
                    }
                    if (data.type == "success") {
                        dialogForm.dialog('close');
                        $$.showModalMessage(data.type, data.message, null);
                        var url_plans = $('#priceplans').children('a').attr('href');
                        document.location = url_plans;
                    }
                }
            });
        }
    });

    $("#addTariffPlan").click(function() {
        var titleDialogForm = $(this).attr("original-title");
        dialogForm.attr("title", titleDialogForm);
        uiDialogTitle.text(titleDialogForm);
        var urlAddPlansAjax = $(this).attr("href");
        $.ajax({
            type: "POST",
            url: urlAddPlansAjax,
            data: {
                mode: "add"
            },
            dataType: "html",
            success: function(data) {
                $('.formContent').html(data);
                $$.utils.forms.resize();
                $$.clientValidate();
            }
        });
        dialogForm.dialog("open");
        return false;
    });

    var editTariffPlan = $(".editTariffPlan");
    editTariffPlan.click(function() {
        var titleDialogForm = $(this).attr("original-title");
        var $this = $(this).attr("href");
        dialogForm.attr("title", titleDialogForm);
        uiDialogTitle.text(titleDialogForm);
        var urlAddPlansAjax = $(this).attr("href");
        $.ajax({
            type: "POST",
            url: urlAddPlansAjax,
            data: {
                mode: "edit"
            },
            dataType: "html",
            success: function(data) {
                $('.formContent').html(data);
                $$.utils.forms.resize();
                $('.formContent form').attr('action', $this);
                dialogForm.dialog("open");
                $$.clientValidate();
            }
        });
        return false;
    });

    $(".showTariffPlan").click(function() {
        var titleDialogForm = $(this).attr("original-title");
        dialogForm.attr("title", titleDialogForm);
        uiDialogTitle.text(titleDialogForm);
        var urlAddPlansAjax = $(this).attr("href");
        $.ajax({
            type: "POST",
            url: urlAddPlansAjax,
            data: {
                mode: "show"
            },
            dataType: "html",
            success: function(data) {
                $('.formContent').html(data);
                $$.utils.forms.resize();
                dialogForm.dialog("open");
            }
        });
        return false;
    });

    // Add group
    $("#addGroupBtn").click(function() {
        //console.log("!!! #addGroupBtn !!!");
        var valid_all = false;
        var group_name = $('input#group_name').val();
        valid_all = group_name.length > 0;
        if (valid_all) {
            var urlAddGroupAjax = $("#addGroup").attr("action");
            //console.log(urlAddGroupAjax);
            var dataAddGroup = $('form#addGroup').serializeObject();
            var dataObject = {};
            dataObject.groupNameField = dataAddGroup;
            console.log(JSON.stringify(dataObject));
            $.ajax({
                type: "POST",
                url: urlAddGroupAjax,
                data: {
                    mode: "add",
                    data: JSON.stringify(dataObject)
                },
                dataType: "html",
                success: function(data) {
                    location.reload();
                }
            });
        } else {
            $('.error_group_name').show().delay(2000).fadeOut();
        }
        return false;
    });

    // Del group
    $(".removeGroupBtn").click(function() {
        if (confirm("Do you really want to delete?")) {
            var urlDelGroupAjax = $(this).attr('data-url');
            console.log(urlDelGroupAjax);
            $.ajax({
                type: "POST",
                url: urlDelGroupAjax,
                data: {
                    mode: "remove"
                },
                dataType: "html",
                success: function(data) {
                    location.reload();
                }
            });
        return false;
        }
    });

    // Edit group
    $("#editGroupBtn").click(function() {
        var urlSaveEditGroupAjax = $("#editGroupForm").attr("action");
        console.log(urlSaveEditGroupAjax);
        var valid_all = false;
        var group_name = $('input#group_name').val();
        valid_all = group_name.length > 0;
        if (valid_all) {
            console.log("Valid!");
            var dataEditGroup = $('form#editGroupForm').serializeObject();
            var dataObject = {};
            dataObject.groupNameField = dataEditGroup;
            console.log(JSON.stringify(dataObject));
            $.ajax({
                type: "POST",
                url: urlSaveEditGroupAjax,
                data: {
                    mode: "save",
                    data: JSON.stringify(dataObject)
                },
                dataType: "html",
                success: function(data) {
                    location.reload();
                }
            });
        }
        return false;
    });

    // ! Set up tooltips
    $$.register('tooltips', ['mylibs/tooltips/jquery.tipsy'], {
        func: function() {
            $('.tooltip').not('.ready').each(function() {
                var $tooltip = $(this),
                    grav = $tooltip.data('gravity') || $.fn.tipsy.autoNS,
                    html = $tooltip.data('html') || false,
                    anim = $tooltip.data('anim') || true,
                    trigger = $tooltip.data('trigger') || 'hover',
                    originalTitle = $tooltip.attr('original-title');

                if (originalTitle == '' || originalTitle === undefined) {
                    $tooltip.attr('original-title', $tooltip.attr('{t}-title'.supplant({
                        t: trigger
                    })));
                }

                $tooltip.tipsy({
                    gravity: grav,
                    fade: anim,
                    html: html,
                    trigger: trigger
                });
            }).addClass('ready');
        },
        init: function() {
            $.fn.tipsy.defaults.opacity = 1;
        },
        check: function() {
            return $('.tooltip').length;
        }
    });

    $('#companySettings input[type=checkbox], #kioskSettings input[type=checkbox]').each(function() {
        if (this.parentNode.parentNode.id != "skipDays") {
            if (this.checked) {
                $(this).val("1")
            } else {
                $(this).val("0");
            }
        }
    });

    if ($('#saleConvertType').prop('checked')) {
        $('#saleConvertPrice').parent().parent().hide();
        $('#saleConvertDays').parent().parent().show();
        $('.onoffswitch-inner').css({
            'margin-left': '0'
        });
        $('.onoffswitch-switch').css({
            'right': '0px'
        });

        if ($('#saleConvertPrice').val() == "") {
            $('#saleConvertPrice').val("1")
        }
    } else {
        $('#saleConvertDays').parent().parent().hide();
        $('#saleConvertPrice').parent().parent().show();
        $('.onoffswitch-inner').css({
            'right': '0px'
        });
        $('.onoffswitch-switch').css({
            'margin-left': '0'
        });
        if ($('#saleConvertDays').val() == "") {
            $('#saleConvertDays').val("0")
        }
    }

    $('#companySettings input[type=checkbox], #kioskSettings input[type=checkbox]').click(function() {
        if (this.parentNode.parentNode.id != "skipDays") {
            if ($(this).prop('checked')) {
                $(this).val("1");
            } else {
                $(this).val("0");
            }
        }
    });

    $('#saleConvertType').click(function() {
        var saleConvertPrice = $('#saleConvertPrice');
        var saleConvertDays = $('#saleConvertDays');
        if ($(this).prop('checked')) {
            $(this).next().next().children('.onoffswitch-inner').removeAttr('style');
            $(this).next().next().children('.onoffswitch-inner').css({
                'margin-left': '0'
            });
            $(this).next().next().children('.onoffswitch-switch').removeAttr('style');
            $(this).next().next().children('.onoffswitch-switch').css({
                'right': '0px'
            });
            saleConvertPrice.parent().parent().hide();
            saleConvertDays.parent().parent().show();
            saleConvertDays.parent().css({
                'height': 'auto'
            });
            if (saleConvertPrice.val() == "") {
                saleConvertPrice.val("1");
            }
        } else {
            $(this).next().next().children('.onoffswitch-inner').removeAttr('style');
            $(this).next().next().children('.onoffswitch-inner').css({
                'right': '0px'
            });
            $(this).next().next().children('.onoffswitch-switch').removeAttr('style');
            $(this).next().next().children('.onoffswitch-switch').css({
                'margin-left': '0'
            });
            saleConvertDays.parent().parent().hide();
            saleConvertPrice.parent().parent().show();
            saleConvertPrice.parent().css({
                'height': 'auto'
            });
            if (saleConvertDays.val() == "") {
                saleConvertDays.val("0");
            }
        }
    });

    if ($('#dvdPreauthMethod').val() == "4") {
        $('#dvdPreauthAmount').parent().parent().show();
    } else {
        $('#dvdPreauthAmount').parent().parent().hide();
    }

    if ($('#bluRayPreauthMethod').val() == "4") {
        $('#bluRayPreauthAmount').parent().parent().show();
    } else {
        $('#bluRayPreauthAmount').parent().parent().hide();
    }

    if ($('#gamePreauthMethod').val() == "4") {
        $('#gamePreauthAmount').parent().parent().show();
    } else {
        $('#gamePreauthAmount').parent().parent().hide();
    }

    $('#dvdPreauthMethod').change(function() {
        if ($(this).val() == '4') {
            $('#dvdPreauthAmount').parent().parent().show();
            $('#dvdPreauthAmount').parent().css({
                'height': 'auto'
            });
        } else {
            $('#dvdPreauthAmount').parent().parent().hide();
        }
    });

    $('#bluRayPreauthMethod').change(function() {
        if ($(this).val() == '4') {
            $('#bluRayPreauthAmount').parent().parent().show();
            $('#bluRayPreauthAmount').parent().css({
                'height': 'auto'
            });
        } else {
            $('#bluRayPreauthAmount').parent().parent().hide();
        }
    });

    $('#gamePreauthMethod').change(function() {
        if ($(this).val() == '4') {
            $('#gamePreauthAmount').parent().parent().show();
            $('#gamePreauthAmount').parent().css({
                'height': 'auto'
            });
        } else {
            $('#gamePreauthAmount').parent().parent().hide();
        }
    });

    $(".f_site_logo").change(function() {
        var $img = $('.f_site_img_logo');
        if (this.files && this.files[0]) {
            var reader = new FileReader();

            reader.onload = function(e) {
                $img.attr('src', e.target.result);
            };

            reader.readAsDataURL(this.files[0]);
        }
    });

    $('#f_create_company .actions input').on('click', function(event) {
        event.preventDefault();
        var companyForm = $('#f_create_company');
        var urlSettings = companyForm.attr('action');

        var dataSettings = companyForm.serializeNestedForms();
            fullLogo = new FormData();
            logo=document.getElementById('f_company_logo').files[0];
            fullLogo.append('f_company_logo', logo);
            fullLogo.append('data', JSON.stringify(dataSettings));
        $.ajax({
            type: "POST",
            url: urlSettings,
            data: fullLogo,
            processData: false,
            contentType: false,
            success: function(data) {
                if (data.type == "error") {
                    $$.showModalMessage(data.type, data.message, null);
                    $$.displayServerValidationResults(data);
                } else if (data.type == "success") {
                    $$.showModalMessage(data.type, data.message, function(){ window.location = data.redirect_url; });
                }
            }
        });
    });

    $('#companySettings .actions input').live('click', function(event) {
        event.preventDefault();
        var urlSettings = $(this).parents('form').attr('action'),
            dataSettings = $('form#companySettings').serializeObject(),
            markedSkipDates = $.map($('[data-mark="delete"][value="1"]'), function(x) {
                return [{
                    'day': x.getAttribute('data-day'),
                    'month': x.getAttribute('data-month'),
                    'year': x.getAttribute('data-year'),
                    'id': x.getAttribute('data-settings-id')
                }]
            });

        $('#companySettings input[type=checkbox]:not(:checked)').each(function() {
            if (this.parentNode.parentNode.id != 'skipDays') {
                var $name = this.name;
                if ($name != "")
                    dataSettings[$name] = this.value;
            }
        });
        dataSettings['languageButtons'] = [];
        $('#companySettings #languageButtons option:selected').each(function() {
            var $val = this.value;
            if ($val != "")
                dataSettings['languageButtons'].push(this.value);
        });
        var dataObject = {};
        dataObject.settings = dataSettings;
        $.ajax({
            type: "POST",
            url: urlSettings,
            data: {
                data: JSON.stringify(dataObject),
                markedSkipDates: JSON.stringify(markedSkipDates)
            },
            dataType: "json",
            success: function(data) {
                if (data.type == "error") {
                    $$.displayServerValidationResults(data);
                } else if (data.type == "success") {
                    $("#dialog_modal").attr('title', data.type);
                    $("#dialog_modal .error").text(data.message);
                    $("#dialog_modal").dialog({
                        autoOpen: false,
                        modal: true,
                        resizable: false,
                        draggable: false,
                        show: null,
                        hide: null
                    }).find('button').click(function() {
                        $(this).parents('.ui-dialog-content').dialog('close');
                        //document.location = urlSettings;
                    });
                    $("#dialog_modal").dialog("open");
                }
            }
        });
    });

    $('#kioskSettings .actions input').live('click', function(event) {
        event.preventDefault();
        var urlSettings = $(this).parents('form').attr('action'),
            dataSettings = $('form#kioskSettings').serializeObject(),
            dataObject = {},
            markedSkipDates = $.map($('[data-mark="delete"][value="1"]'), function(x) {
                return [{
                    'day': x.getAttribute('data-day'),
                    'month': x.getAttribute('data-month'),
                    'year': x.getAttribute('data-year'),
                    'id': x.getAttribute('data-settings-id')
                }]
            });

        dataSettings['languageButtons'] = [];
        $('#kioskSettings input[type=checkbox]:not(:checked)').each(function() {
            if (this.parentNode.parentNode.id != 'skipDays') {
                var $name = this.name;
                if ($name != "") {
                    dataSettings[$name] = this.value;
                }
            }
        });
        $('#kioskSettings #languageButtons option:selected').each(function() {
            var $val = this.value;
            if ($val != "")
                dataSettings['languageButtons'].push(this.value);
        });

        var domSchedule = $('#kioskSettings').find('.scheduler .right select option'),
            schedule = domSchedule.map(function() {
                return this.getAttribute('data-id');
            }).toArray();
        dataSettings['schedule'] = schedule;


        dataObject.settings = dataSettings;
        $.ajax({
            type: "POST",
            url: urlSettings,
            data: {
                data: JSON.stringify(dataObject),
                markedSkipDates: JSON.stringify(markedSkipDates)
            },
            dataType: "json",
            success: function(data) {
                if (data.type == "error") {
                    // here results displaying are specific - think of adding second param (condition)
                    // to handle that if it is necessary.
                    var errors = $(data.errors);
                    var resetInputs = $("form input");
                    resetInputs.removeClass('error');
                    errors.each(function(idx, val) {
                        var input = $('#' + val.field);
                        if (input.next().attr('class') == undefined) {
                            input.after('<div class="error-icon icon" style="right: 5.99998px; top: 33.5px;"></div>');
                        }
                        if (input.next().next().attr('class') == undefined) {
                            input.next().after('<label class="error inline" for="' + val.field + '" style="top: -15px;">' + val.message + '</label>');
                        } else {
                            input.next().next().text(val.message);
                        }
                        input.next().next().show();
                        input.next().next().addClass('inline');
                        input.next().next().css({
                            'top': '-15px'
                        });
                        if (val.field != 'languageButtons') {
                            input.next().removeClass('valid-icon');
                            input.next().addClass('error-icon');
                        }
                    });
                } else if (data.type == "success") {
                    $("#dialog_modal").attr('title', data.type);
                    $("#dialog_modal .error").text(data.message);
                    $("#dialog_modal").dialog({
                        autoOpen: false,
                        modal: true,
                        resizable: false,
                        draggable: false,
                        show: null,
                        hide: null
                    }).find('button').click(function() {
                        $(this).parents('.ui-dialog-content').dialog('close');
                        document.location = data.redirect_url;
                    });
                    $("#dialog_modal").dialog("open");
                }
            }
        });
    });

    $('#kioskReview .actions input#start').on('click', function(event) {
        event.preventDefault();
        var urlReview = $(this).parents('form').attr('action'),
            dataReview = $('form#kioskReview select#kiosks').serializeObject(),
            dataObject = {};

        dataReview['loadDB'] = $('#kioskReview input[type=checkbox]').is(':checked');
        //var domKiosks = $('#kioskReview').find('.kiosksStartReview .right select option'),
        //    kiosksStartReview = domKiosks.map(function() {
        //        return this.getAttribute('data-id');
        //    }).toArray();

        //dataReview['kiosksStartReview'] = kiosksStartReview;

        dataObject.review = dataReview;
        $.ajax({
            type: "POST",
            url: urlReview,
            data: {
                data: JSON.stringify(dataObject),
            },
            dataType: "json",
            success: function(data) {
                if (data.type == "error") {
                    // here results displaying are specific - think of adding second param (condition)
                    // to handle that if it is necessary.
                    var errors = $(data.errors);
                    var resetInputs = $("form input");
                    resetInputs.removeClass('error');
                    errors.each(function(idx, val) {
                        var input = $('#' + val.field);
                        if (input.next().attr('class') == undefined) {
                            input.after('<div class="error-icon icon" style="right: 5.99998px; top: 33.5px;"></div>');
                        }
                        if (input.next().next().attr('class') == undefined) {
                            input.next().after('<label class="error inline" for="' + val.field + '" style="top: -15px;">' + val.message + '</label>');
                        } else {
                            input.next().next().text(val.message);
                        }
                        input.next().next().show();
                        input.next().next().addClass('inline');
                        input.next().next().css({
                            'top': '-15px'
                        });
                    });
                } else if (data.type == "success") {
                    $("#dialog_modal").attr('title', data.type);
                    $("#dialog_modal .error").text(data.message);
                    $("#dialog_modal").dialog({
                        autoOpen: false,
                        modal: true,
                        resizable: false,
                        draggable: false,
                        show: null,
                        hide: null
                    }).find('button').click(function() {
                        $(this).parents('.ui-dialog-content').dialog('close');
                        document.location = data.redirect_url;
                    });
                    $("#dialog_modal").dialog("open");
                }
            }
        });
    });
    $('#kioskReview .actions input#stop').on('click', function(event) {
        event.preventDefault();
        var urlReview = $(this).parents('form').attr('action'),
            dataReview = $('form#kioskReview select#kiosksStop').serializeObject(),
            dataObject = {};
        console.log(dataReview);
        //dataReview.serializeObject();
        console.log(dataReview);

        dataObject.review = dataReview;
        $.ajax({
            type: "POST",
            url: urlReview,
            data: {
                data: JSON.stringify(dataObject),
            },
            dataType: "json",
            success: function(data) {
                if (data.type == "error") {
                    // here results displaying are specific - think of adding second param (condition)
                    // to handle that if it is necessary.
                    var errors = $(data.errors);
                    var resetInputs = $("form input");
                    resetInputs.removeClass('error');
                    errors.each(function(idx, val) {
                        var input = $('#' + val.field);
                        if (input.next().attr('class') == undefined) {
                            input.after('<div class="error-icon icon" style="right: 5.99998px; top: 33.5px;"></div>');
                        }
                        if (input.next().next().attr('class') == undefined) {
                            input.next().after('<label class="error inline" for="' + val.field + '" style="top: -15px;">' + val.message + '</label>');
                        } else {
                            input.next().next().text(val.message);
                        }
                        input.next().next().show();
                        input.next().next().addClass('inline');
                        input.next().next().css({
                            'top': '-15px'
                        });
                    });
                } else if (data.type == "success") {
                    $("#dialog_modal").attr('title', data.type);
                    $("#dialog_modal .error").text(data.message);
                    $("#dialog_modal").dialog({
                        autoOpen: false,
                        modal: true,
                        resizable: false,
                        draggable: false,
                        show: null,
                        hide: null
                    }).find('button').click(function() {
                        $(this).parents('.ui-dialog-content').dialog('close');
                        document.location = data.redirect_url;
                    });
                    $("#dialog_modal").dialog("open");
                }
            }
        });
    });


    var day = new Date(),
        monthNames = [
            'January', 'February',
            'March', 'April', 'May',
            'June', 'July', 'August',
            'September', 'October', 'November',
            'December'
        ],
        skipPeriodsSelectors = document.querySelector('#skipPeriods'),
        dateSelector = skipPeriodsSelectors !== null ?
            skipPeriodsSelectors.querySelector('[data-id="skipPeriod"]') :
            null,
        addSkipPeriod = skipPeriodsSelectors !== null ?
            skipPeriodsSelectors.querySelector('#addSkipPeriod') :
            null;

    if (addSkipPeriod !== null)
        addSkipPeriod.addEventListener('click', function(e) {
            e.stopPropagation();
            dateSelector = createDateSelector()
            $(addSkipPeriod).before(dateSelector)
        }, false);


    // live removal of row from datatables
    // table.dataTable().fnDeleteRow(row[0])
    // where row[0] - just plain old HTML for row to remove
    $("a[data-id='deleteSkipDate']").on('click', function() {
        var row = $(this).closest('tr'),
            table = $('[data-id="skipDates"]'),
            rows = table.find('tr');
        $.ajax({
            type: "POST",
            url: row.attr('data-url'),
            data: {
                day: row.attr('data-day'),
                month: row.attr('data-month'),
                year: row.attr('data-year'),
                settingsId: row.attr('data-settings-id')
            },
            dataType: "json",
            success: function() {},
            error: function() {
                alert("Error during deleting skip date");
            }
        });
    });

    $('input[data-mark="delete"]').on('change', function() {
        var skipDate = $(this).closest('tr'),
            elements = skipDate.find('td');
        elements.toggleClass('strike-out')
    });

    // Example of live search
    $('#upcLink_chosen .chosen-search input,#upcLink2_chosen .chosen-search input').live('keyup', function(event) {
        // home $, end #
        if (/[a-zA-Z0-9-_.]/.test(String.fromCharCode(event.keyCode))) {
            var upc_select = document.querySelector('#upcLink');
            if (upc_select == null) {
                upc_select = document.querySelector('#upcLink2');
            }

            var upc_chosen = $('#upcLink_chosen');
            if (upc_chosen.length == 0) {
                upc_chosen = $('#upcLink2_chosen');
            }
            $.ajax({
                type: "GET",
                url: upc_select.getAttribute('data-search-url'),
                data: {
                    'upcLink': $(this).val()
                },
                dataType: "json",
                success: function(data) {
                    var chosenSearch = upc_chosen.find('.chosen-search input');
                    var searchSelect = document.querySelector('select#upcLink');
                    if (searchSelect == null) {
                        searchSelect = document.querySelector('select#upcLink2');
                    }
                    var searchVal = chosenSearch.val();
                    searchSelect.options.length = 0;
                    searchSelect.appendChild(new Option('', ''))
                    if (data.upcs.length > 0) {
                        for (var i = 0, len = data.upcs.length; i < len; i++) {
                            searchSelect.appendChild(new Option(data.upcs[i], data.upcs[i]))
                        }
                    } else {
                        var noMatch = new Option('No results match "' + data.query + '"')
                        noMatch.disabled = true
                        searchSelect.appendChild(noMatch)
                    }
                    if (parseInt(data.upcs_amount) > 0) {
                        var extra = new Option('And ' + data.upcs_amount + ' others...', '');
                        extra.disabled = true
                        searchSelect.appendChild(extra)
                    }
                    $(searchSelect).trigger('chosen:updated')
                    chosenSearch.val(searchVal)
                },
                error: function() {
                    alert("Error during search");
                }
            })
        }
    });

    $("#addUpcTariff").dialog({
        autoOpen: false,
        modal: true,
        resizable: false,
        draggable: false,
        width: 500,
        open: function() {
            $(this).parent().css('overflow', 'visible');
            $$.utils.forms.resize()
        }
    });

    $("#upcTransfer").dialog({
        autoOpen: false,
        modal: true,
        resizable: false,
        draggable: false,
        width: 600,
        open: function() {
            $(this).parent().css('overflow', 'visible');
            $$.utils.forms.resize()
        }
    }).find('button.cancel').live('click', function() {
        $(this).parents('.ui-dialog-content').dialog('close')
    });

    var linkDL = $('#addDisc #upcLink');
    linkDL.focus();
    $('#addDisc #upcLink').on('keypress', function(event) {
        if (event.keyCode == 13 || event.keyCode == 9) {
            var url = $('#addDisc #upcLink').parents('form').attr('data-upc-url'),
                upcField = $(this),
                upcLink = upcField.val();

            if (!upcLink == "") {
                $.ajax({
                    type: "GET",
                    url: url,
                    data: {
                        'upcLink': upcLink
                    },
                    dataType: "json",
                    success: function(data) {
                        addNotification(data)
                        if (data.type == "success") {
                            $('#diskInfo').html(data.data.html);
                            var checkTariffBox = $('#addUpcTariff'),
                                checkTariffUrl = checkTariffBox.attr('data-check-tariff-url').replace('0', upcLink);
                            $.ajax({
                                type: "GET",
                                url: checkTariffUrl,
                                dataType: 'json',
                                success: function(data) {
                                    if (data.type == "success") {
                                        $('#rfId').focus();
                                    } else if (data.type == "warning") {
                                        checkTariffBox.removeClass('invisible')
                                        checkTariffBox.html(data.data.modal_html)
                                        $('#tariffPlanId').chosen({
                                            'width': '100%'
                                        });
                                        checkTariffBox.dialog("open");
                                    }
                                },
                                error: function() {
                                    alert("Error! Can not check tariff plan.");
                                }
                            })
                        } else if (data.type == "error") {
                            upcField.select()
                            $('#diskInfo').html('');
                        }
                    },
                    error: function() {
                        alert("Error! Extended info isn't shown.");
                    }
                });
            }
        }
    });

    $('#addDisc #upcLink').on('change', function(evt, params) {
        if (typeof(params) == "undefined")
            $('#diskInfo').html('');
    });

    $('#addUpcTariff').on('click', '.actions .right input[type="submit"]', function(e) {
        e.preventDefault();
        var form = $('#upcMissingTariffAssign'),
            upcTariffUrl = form.attr('action'),
            tariff = form.serializeObject();
        $.ajax({
            type: "POST",
            url: upcTariffUrl,
            data: tariff,
            dataType: "json",
            success: function(data) {
                var success_function = null;
                if (data.type == 'success'){
                    success_function = function(){
                        $('#addUpcTariff').dialog('close');
                        $('#rfId').focus()
                    };
                }

                addNotification(data);

                $$.showModalMessage(data.type, data.message, success_function);
            },
            error: function() {
                alert("FAIL! Cannot add tariff to UPC.")
            }
        })
    })

    $('#upcTransfer .actions .right button#reassign').live('click', reassignDisk)

    $('#addDiskBox .actions input[type=submit]').click(addDisk);
    $('#addDiskBox #rfId').on('keyup', function(event) {
        if (event.keyCode == 13) addDisk(event)
    });
    var dealsTr = $('#deals-table:not(.all-deals) tbody tr');

    dealsTr.click(function() {
        var that = this;
        var id = $(this).attr('data-id');
        var url = $(this).attr('data-url');
        var oTable = $('#deals-table').dataTable();

        if (oTable.fnIsOpen(this)) {
            oTable.fnClose(this);
            $(that).children('td').removeAttr('style');
        } else {
            $.ajax({
                type: "GET",
                url: url,
                data: {},
                success: function(data) {
                    oTable.fnOpen(that, data, "info_row");
                    $$.utils.forms.resize();
                    $(that).children('td').css({
                        'background-color': '#2c3747',
                        'color': '#ffffff'
                    });
                    $.each($('input[data-operate="inline"]'), function() {
                        this.style.width = this.value.length * 6 + 'px';
                    });

                    $.each($('select[data-operate="inline"]'), function() {
                        $(this).chosen({
                            disable_search: true
                        })
                    });
                }
            });
        }
    });

    $('#deals-table.all-deals tbody').on('click', 'tr.dt-row-click', function() {
        var that = this;
        var id = $(this).attr('id');
        var url = $('#data-url').val().replace('replace', id);
        var oTable = $('#deals-table').dataTable();

        if (oTable.fnIsOpen(this)) {
            oTable.fnClose(this);
            $(that).children('td').removeAttr('style');
        } else {
            $.ajax({
                type: "GET",
                url: url,
                data: {},
                success: function(data) {
                    oTable.fnOpen(that, data, "info_row");
                    $$.utils.forms.resize();
                    $(that).children('td').css({
                        'background-color': '#2c3747',
                        'color': '#ffffff'
                    });
                    $.each($('input[data-operate="inline"]'), function() {
                        this.style.width = this.value.length * 6 + 'px';
                    });

                    $.each($('select[data-operate="inline"]'), function() {
                        $(this).chosen({
                            disable_search: true
                        })
                    });
                }
            });
        }
    });

    $('tr[data-permission="All"] td input[type="checkbox"]').on('change', function(event) {
        var dataCheckGroup = $(this).closest('td').attr('data-check-group');
        $(this).parents('table').find('td[data-check-group=' + dataCheckGroup + '] input[type="checkbox"]').attr('checked', $(this).attr('checked') || false)
    });

    $('tr[data-permission="Specific"] td input[type="checkbox"]').on('change', function(event) {
        var dataCheckGroup = $(this).closest('td').attr('data-check-group');
        $('tr[data-permission="All"] td[data-check-group=' + dataCheckGroup + '] input[type="checkbox"]').attr('checked', false)
    });
    $('[data-id="permToCompany"], [data-id="removeCompanyPerm"]').on('click', function(e) {
        e.preventDefault();
        if (e.target.tagName != 'A') {
            var url = $(e.target).closest('a').attr('data-url');
        } else {
            var url = e.target.getAttribute('data-url');
        }
        $.ajax({
            type: "POST",
            url: url,
            dataType: "json",
            success: function(data) {
                window.location.href = data.redirect_url
            },
            error: function() {
                alert("FAIL!")
            }
        })
    });

    var oldUrl = $('#finishTransaction').attr('action');
    $("#finishDealModal").dialog({
        autoOpen: false,
        resizable: false,
        draggable: false,
        modal: true,
        width: 400,
        open: function() {
            $(this).parent().css('overflow', 'visible');
            $$.utils.forms.resize();
        }
    }).find('button.cancel').click(function() {
        var $el = $(this).parents('.ui-dialog-content');
        $el.find('form')[0].reset();
        $el.dialog('close');
    });
    var newInput = $("#dtEnd").parent().html();

    $('#deals-table [data-id="finishDealBtn"]').live('click', function(e) {
        e.preventDefault();
        var type = $(this).attr('data-type');
        $('#type').val(type);
        var title = $(this).attr('data-title');
        uiDialogTitle.html(title);
        var dealId = $(this).attr('data-deal-id');
        var newurl = oldUrl.replace('0', dealId);
        $('#finishTransaction').attr('action', newurl);
        var daySeconds = Number($(this).attr('data-date'));
        var startDate = new Date();
        var endDate = new Date();
        var timeZone = $(this).attr('data-timezone');
        var offSet = new Date().getTimezoneOffset();
        startDate.setTime(daySeconds - (timeZone - offSet) * 60 * 1000);
        endDate.setTime(endDate.getTime() - (timeZone - offSet) * 60 * 1000);
        $("#dtEnd").remove();
        $('#finishTransaction').children().children().children('div').html(newInput);
        $("#dtEnd").removeClass('hasDatepicker');
        $.timepicker._defaults.hourMax = 23;
        $.timepicker._defaults.hourMin = 0;
        $.timepicker._defaults.minuteMax = 59;
        $.timepicker._defaults.minuteMin = 0;
        $.timepicker._defaults.minDateTime = null;
        $.timepicker._defaults.maxDateTime = null;
        $.timepicker._defaults.minDate = null;
        $.timepicker._defaults.maxDate = null;
        $("#dtEnd").datetimepicker({
            maxDateTime: endDate,
            minDateTime: startDate
        });
        $('#finishDealModal').dialog('open');
    });

    $('#deals-table [data-id="finishDealVoidBtn"]').live('click', function(e) {
        e.preventDefault();
        var target = e.target;
        console.log(target.getAttribute('data-url'))
        $.ajax({
            type: "POST",
            url: target.getAttribute('data-url'),
            success: function(data) {
                $("#dialog_modal").attr('title', data.type);
                $("#dialog_modal .error").text(data.message);
                $("#dialog_modal").dialog({
                    autoOpen: false,
                    modal: true,
                    resizable: false,
                    draggable: false
                }).find('button').click(function() {
                    $(this).parents('.ui-dialog-content').dialog('close');
                    window.location = data.redirect_url
                });
                $("#dialog_modal").dialog("open");

            },
            error: function() {
                alert("FAIL")
            }
        });
    });

    $('#sendEmailForRestorePassword').on('click', function(e) {
        e.preventDefault();
        var form = $('#formSendEmailForRestorePassword'),
            data = form.serializeObject(),
            url = form.attr('action');
        $.ajax({
            type: "POST",
            url: url,
            data: data,
            dataType: "json",
            success: function(data) {
                alert(data.message);
            },
            error: function() {
                alert("ERROR!");
            }
        });
    });

    $('#replayDeal').on('click', function(e) {
        e.preventDefault();
        var form = $('#finishTransaction'),
            data = form.serializeObject(),
            url = form.attr('action');
        $.ajax({
            type: "POST",
            url: url,
            data: data,
            dataType: "json",
            success: function(data) {
                if (data.type == "success") {
                    window.location = data.redirect_url
                }
            },
            error: function() {
                alert("ERROR!")
            }
        })
        var $el = $(this).parents('.ui-dialog-content');
        $el.find('form')[0].reset();
        $el.dialog('close');
    })

    $('#kioskTariffValues .actions .left #revertTariff').on('click', function(e) {
        var url = $('#kioskTariffValues').attr('data-revert-url');
        $.ajax({
            type: "POST",
            url: url,
            dataType: "json",
            success: function(data) {
                if (data.type == "success") {
                    window.location = data.redirect_url
                } else if (data.type == "error") {
                        $$.displayServerValidationResults(data);
                }
            },
            error: function() {
                alert("ERROR!");
            }
        })
    });

     $('#btnKioskTariffValues').on('click', function(e) {
        e.preventDefault();
        var form = $('#kioskTariffValues'),
            data = form.serializeObject(),
            url = form.attr('action');
        $.ajax({
            type: "POST",
            url: url,
            data: data,
            dataType: "json",
            success: function(data) {
                if (data.type == "success") {
                    window.location.reload();
                } else if (data.type == "error") {
                    var errors = $(data.errors);
                    var resetInputs = $("form input");
                    errors.each(function(idx, val) {
                        var input = $('#' + val.field);
                        if (input.next().attr('class') == undefined) {
                            input.after('<div class="error-icon icon" style="right: 5.99998px; top: 33.5px;"></div>');
                        }
                        if (input.next().next().attr('class') == undefined) {
                            input.next().after('<label class="error inline" for="' + val.field + '" style="top: -15px;">' + val.message + '</label>');
                        } else {
                            input.next().next().text(val.message);
                        }
                        input.next().next().show();
                        input.next().next().addClass('inline');
                        input.next().next().css({
                            'top': '-15px'
                        });
                        input.next().removeClass('valid-icon');
                        input.next().addClass('error-icon');
                    });
                }
            },
            error: function() {
                alert("ERROR!");
            }
        })
    });

    $('#movieTranslation').on('change', function(e) {
        e.preventDefault();
        if (this.value) {
            var selected = this.options[this.selectedIndex],
                lang = selected.text;
            addMovieTranslation(lang, this.value);
            selected.disabled = true;
            $(this).val('').trigger('chosen:updated');
        }
    });

    $('#movieTranslations').on('click', '.discard-translation', function(e) {
        e.preventDefault();
        var lang_name = $(this).parent().parent().find('input[name="id"]').val();
        $(this).parent().parent().remove();

        var option = $('option[value="' + lang_name + '"]');
        option.removeAttr('disabled');
        $('#movieTranslation').trigger('chosen:updated');
    });

    $('#addMovieBox .actions .right input[type="submit"]').on('click', function(e) {
        e.preventDefault();
        var form = $('#addMovie'),
            url = form.attr('action'),
            //movie = form.serializeNestedForms(),
            movie = form.serializeObject();
            coverFile = document.getElementById('imgPath').files[0],
            fullMovieInfo = new FormData();

        movie['translations'] = [];
        $.each($('#movieTranslations .trans-form'), function(idx, val){
            movie['translations'].push($(val).serializeObject());
        });
        fullMovieInfo.append('cover', coverFile);
        fullMovieInfo.append('movie', JSON.stringify(movie));
        $.ajax({
            type: "POST",
            url: url,
            data: fullMovieInfo,
            processData: false,
            contentType: false,
            success: function(data) {
                var close_function = null;

                if (data.type == "error") {
                    $$.displayServerValidationResults(data)
                }

                if (data.type == "success" & data.redirect_url != '') {
                    close_function = function () { window.location = data.redirect_url;};
                }

                $$.showModalMessage(data.type, data.message, close_function);
            },
            error: function() {
                alert("FAIL!")
            }
        })
    })

    $('#createUpcBox .actions .right input[type="submit"]').on('click', function(e) {
        e.preventDefault();
        var form = $('#createUpc'),
            url = form.attr('action'),
            upcData = form.serializeObject();
        $.ajax({
            type: "POST",
            url: url,
            data: upcData,
            dataType: 'json',
            success: function(data) {
                addNotification(data)
                if (data.type == "error") {
                    $$.displayServerValidationResults(data)
                }
            },
            error: function() {
                alert("FAIL!")
            }
        })
    })

    $('#movieId_chosen .chosen-search input').live('keyup', function(event) {
        // home $, end #
        if (/[a-zA-Z0-9-_.]/.test(String.fromCharCode(event.keyCode))) {
            var movie_select = document.querySelector('#movieId');

            var movie_chosen = $('#movieId_chosen');
            $.ajax({
                type: "GET",
                url: movie_select.getAttribute('data-search-url'),
                data: {
                    'movie': $(this).val()
                },
                dataType: "json",
                success: function(data) {
                    var chosenSearch = movie_chosen.find('.chosen-search input');
                    var searchSelect = document.querySelector('select#movieId');
                    var searchVal = chosenSearch.val();
                    searchSelect.options.length = 0;
                    searchSelect.appendChild(new Option('', ''))
                    if (data.movies.length > 0) {
                        for (var i = 0, len = data.movies.length; i < len; i++) {
                            searchSelect.appendChild(new Option(data.movies[i][1], data.movies[i][0]))
                        }
                    } else {
                        var noMatch = new Option('No results match "' + data.query + '"')
                        noMatch.disabled = true
                        searchSelect.appendChild(noMatch)
                    }
                    if (parseInt(data.movies_amount) > 0) {
                        var extra = new Option('And ' + data.movies_amount + ' others...', '');
                        extra.disabled = true
                        searchSelect.appendChild(extra)
                    }
                    $(searchSelect).trigger('chosen:updated')
                    chosenSearch.val(searchVal)
                },
                error: function() {
                    alert("Error during search");
                }
            })
        }
    });

    $('#moviesUpdate').on('click', function() {
        var updateBtn = $(this),
            produceUrl = updateBtn.attr('data-produce-url'),
            last_response_len = false,
            detailedInfo = document.getElementById('updateDetailedInfo'),
            date = $('.date-changed #date'),
            status = $('.date-changed #status');
        $(detailedInfo).empty()
        if (!updateBtn.prop('disabled')) {
            updateBtn.prop('disabled', true)
            date.text(new Date().toLocaleString())
            status.text('partial')
            $.ajax({
                type: "POST",
                url: produceUrl,
                dataType: "json",
                success: function(data) {
                    if (data.type == "error") {
                        //console.log(data)
                        alert(data.message)
                    }
                },
                error: function() {
                    updateBtn.prop('disabled', false)
                    //console.log("ERROR: Smth went wrong, can not update.");
                }
            })
        }
    });

    //////////////////////////////////////////////////
    //        Transactions manual editing           //
    //////////////////////////////////////////////////
    var dealsRestrictedFields = ['dealTypeId', 'firstNight', 'nextNight', 'totalDays', 'sale'],
        isChanged = function() {
            return $(this).data('changed') == true
        },
        lockEditing = function(totalAmountChanged) {
            if (totalAmountChanged) {
                for (val in dealsRestrictedFields) {
                    $('[data-field="' + dealsRestrictedFields[val] + '"]').addClass('hidden');
                }
            } else {
                $('[data-field="totalAmount"]').addClass('hidden');
            }
        };

    $('#deals-table .icon-pencil').live('click', function(e) {
        e.preventDefault();
        var parent = $(e.target.parentNode.parentNode),
            input = parent.find('[data-operate="inline"]'),
            fieldActions = parent.find('[data-field]'),
            visibleContent = fieldActions.find(':not(.hidden)'),
            hiddenContent = fieldActions.find('.hidden');

        lockEditing(input.attr('name') == 'totalAmount');

        input.data('value', input.val());
        input.prop('disabled', false);
        input.select()
        hiddenContent.removeClass('hidden');
        visibleContent.addClass('hidden');
        if (input.prop('tagName') == 'SELECT')
            input.trigger('chosen:updated')
    });

    $('#deals-table .icon-ok').live('click', function(e) {
        e.preventDefault();
        var parent = $(e.target.parentNode.parentNode),
            input = parent.find('[data-operate="inline"]'),
            totalAmountChanged = input.attr('name') == 'totalAmount',
            form = $(e.target).parents('form'),
            tax = parseFloat(form.attr('data-tax')) / 100,
            actions = form.find('.actions'),
            fieldActions = parent.find('[data-field]'),
            visibleContent = fieldActions.find(':not(.hidden)'),
            hiddenContent = fieldActions.find('.hidden'),
            dealType = parseInt(form.find('[name="dealTypeId"]').find('option[selected]').val()),
            firstNight = parseFloat(form.find('[name="firstNight"]').val()),
            nextNight = parseFloat(form.find('[name="nextNight"]').val()),
            totalDays = parseFloat(form.find('[name="totalDays"]').val()),
            sale = parseFloat(form.find('[name="sale"]').val()),
            totalAmount = form.find('[name="totalAmount"]');

        lockEditing(totalAmountChanged);

        if (!totalAmountChanged) {
            if (dealType == 1) {
                if (totalDays == 0) {
                    totalAmount.val((0).toFixed(2))
                } else {
                    totalAmount.val(((1 + tax) * (firstNight + (totalDays - 1) * nextNight)).toFixed(2));
                }
            } else if (dealType == 2) {
                totalAmount.val(((1 + tax) * sale).toFixed(2));
            }
        }

        actions.removeClass('hidden');
        input.attr('value', input.val());
        input.data('changed', true);
        if (input.val() == input.attr('data-original-value'))
            input.data('changed', false);
        if ($('[data-operate="inline"]').filter(isChanged).length == 0) {
            actions.addClass('hidden');
            $('[data-field]').removeClass('hidden');
        }
        input.prop('disabled', true);
        hiddenContent.removeClass('hidden');
        visibleContent.addClass('hidden');
        if (input.prop('tagName') == 'SELECT')
            input.trigger('chosen:updated')
        $.each($('input[data-operate="inline"]'), function() {
            this.style.width = this.value.length * 6 + 'px';
        })
    });

    $('#deals-table .icon-remove').live('click', function(e) {
        e.preventDefault();
        var parent = $(e.target.parentNode.parentNode),
            input = parent.find('[data-operate="inline"]'),
            fieldActions = parent.find('[data-field]'),
            visibleContent = fieldActions.find(':not(.hidden)'),
            hiddenContent = fieldActions.find('.hidden');

        input.val(input.data('value'));
        input.prop('disabled', true);
        hiddenContent.removeClass('hidden');
        visibleContent.addClass('hidden');
        if (input.prop('tagName') == 'SELECT')
            input.trigger('chosen:updated')
        if ($('[data-operate="inline"]').filter(isChanged).length == 0)
            $('[data-field]').removeClass('hidden');
        $.each($('input[data-operate="inline"]'), function() {
            this.style.width = this.value.length * 6 + 'px';
        })
    });

    $('#deals-table button[data-id="manualChange"]').live('click', function(e) {
        e.preventDefault();
        var target = e.target,
            form = $(target).parents('form'),
            infoRow = $(target).closest('tr'),
            infoCell = infoRow.find('td'),
            inputs = form.find('[data-operate="inline"]'),
            actions = form.find('[data-id="actions"]'),
            refreshDealInfo = false,
            changedFields = {};

        var dealInfoUrl = '';
        if ($('#data-url') != 'undefined'){
            dealInfoUrl = $('#data-url').val().replace('replace', infoRow.prev().attr('id'));
        } else {
            dealInfoUrl = infoRow.prev().attr('data-url');
        }

        for (var i = 0, len = inputs.length; i < len; i++) {
            var jqInput = $(inputs[i]);
            if (jqInput.data('changed')) {
                changedFields[jqInput.attr('name')] = inputs[i].value
                if (jqInput.attr('name') == 'dealTypeId')
                    refreshDealInfo = true;
            }
        }

        $.ajax({
            type: "POST",
            url: form.attr('data-url'),
            data: changedFields,
            dataType: "json",
            success: function(data) {
                // modal here
                if (data.type == "success") {
                    actions.addClass('hidden')
                    var openedRow = infoRow.prev();
                    openedRow.find('[data-field="status"]').html(data.data.status);
                    if (refreshDealInfo) {
                        $.ajax({
                            type: "GET",
                            url: dealInfoUrl,
                            data: {},
                            success: function(data) {
                                infoCell.html(data);
                                $$.utils.forms.resize();
                                $.each($('input[data-operate="inline"]'), function() {
                                    this.style.width = this.value.length * 6 + 'px';
                                });

                                $.each($('select[data-operate="inline"]'), function() {
                                    $(this).chosen({
                                        disable_search: true
                                    })
                                });
                            }
                        });
                    }
                    alert(data.message)
                } else if (data.type == "error") {
                    alert(data.message)
                }
            },
            error: function() {
                alert("Error during manual change of deal!")
            }
        })
    })

    $('#deals-table button[data-id="manualChangeCancel"]').live('click', function(e) {
        e.preventDefault();
        var target = e.target,
            form = $(target).parents('form'),
            actions = form.find('.actions'),
            inputs = form.find('[data-operate="inline"]'),
            fieldActions = form.find('[data-field]');

        for (var i = 0, len = inputs.length; i < len; i++) {
            var jqInput = $(inputs[i]);
            if (jqInput.data('changed'))
                jqInput.val(jqInput.data('value'));
            if (jqInput.prop('tagName') == 'SELECT')
                jqInput.trigger('chosen:updated');
        }

        actions.addClass('hidden');
        fieldActions.removeClass('hidden');
    });

    $('#makeScreen').on('click', function(e) {
        var button = e.target,
            url = button.getAttribute('data-url'),
            latestTop = $('#latestTop'),
            latestBottom = $('#latestBottom'),
            loading = $('.latest-screen #loading'),
            loadingOverlay = $('.latest-screen #loading-overlay'),
            images = $('#screenGallery .image'),
            makeScreenBtn = $('#makeScreen');
        latestTop.addClass('hidden');
        latestBottom.addClass('hidden');
        loading.removeClass('hidden');
        loadingOverlay.removeClass('hidden');
        makeScreenBtn.prop('disabled', true)
        $.ajax({
            type: "POST",
            url: url,
            success: function(data) {
                // modal here
                if (data.type == 'success') {
                    images.slice(-2).remove()
                    makeScreenBtn.prop('disabled', false)
                    latestTop.find('a').attr('href', data.data.topScreen)
                    latestBottom.find('a').attr('href', data.data.bottomScreen)
                    latestTop.find('img').attr('src', data.data.topScreen)
                    latestBottom.find('img').attr('src', data.data.bottomScreen)
                    latestTop.removeClass('hidden');
                    latestBottom.removeClass('hidden');
                    var bottomClone = latestBottom.clone(),
                        topClone = latestTop.clone();
                    bottomClone.removeAttr('id');
                    bottomClone.prependTo("#screenGallery");
                    topClone.removeAttr('id');
                    topClone.prependTo("#screenGallery");
                    loading.addClass('hidden');
                    loadingOverlay.addClass('hidden');
                } else if (data.type == 'error') {
                    alert(data.message);
                }
            },
            error: function() {
                alert("ERROR! Something went wrong!")
            }
        })
    })
    ////////////////////////////////////////////////////////////////////
    //              End of transactions manual editing                //
    ////////////////////////////////////////////////////////////////////

    // Profile script
    $('#profileChange').on('click', function(e) {
        e.preventDefault();
        var $target = $(e.target);
        $.ajax({
            type: "POST",
            data: $target.closest('form').serializeObject(),
            dataType: "json",
            success: function(data) {
                if (data.type == "error") {
                    $$.displayServerValidationResults(data)
                } else if (data.type == "success") {
                    window.location.href = data.redirect_url
                }
            },
            error: function() {
                alert("Error during sending request!");
            }
        })
    })

    // Featured movies
    $('#featuredMovies #movieId').on('change', function(e, params) {
        var shortInfo = $('#shortMovieInfo');
        if (params !== undefined) {
            var movieId = parseInt(params['selected']),
                url = e.target.getAttribute('data-short-info-url').replace(0, movieId);
            $.ajax({
                type: "GET",
                url: url,
                data: {
                    'movie_id': movieId
                },
                dataType: "html",
                success: function(data) {
                    shortInfo.html(data);
                }
            })
        } else {
            shortInfo.html('');
        }
    })

    $('#makeFeatured').on('click', function(e) {
        e.preventDefault();
        var formData = $('#featuredMovies').serializeObject();
        $('#shortMovieInfo').html('');
        $.ajax({
            type: "POST",
            data: formData,
            dataType: "json",
            success: function(data) {
                $$.showModalMessage(data.type, data.message, null);
                if (data.type == "success") {
                    var table = $('#featuredMoviesTable'),
                        url = table.attr('data-unfeature-url').replace(0, data.data.movieId),
                        link = $('<a class="button small grey" href="' + url + '"><i class="icon-remove"></i></a>');
                    var options = [
                        data.data.id,
                        data.data.name,
                        data.data.length,
                        data.data.release,
                        data.data.releaseDvd,
                        link.wrap('<div>').parent().html()
                    ];
                    table.dataTable({
                        "bRetrieve": true
                    }).fnAddData(options);
                }
            },
            error: function() {
                alert("Error! Can't make featured!")
            }
        })
    });

    $('#bindSiteToCompany').on('click', function(e) {
        e.preventDefault();
        var form = $('form#companySite')
        var formData = form.serializeObject(),
            logo = document.getElementById('logo').files[0],
            url = form.attr('action'),
            siteInfo = new FormData();
        console.log(url);
        siteInfo.append('site', JSON.stringify(formData));
        siteInfo.append('logo', logo);
        console.log(url);
        $.ajax({
            type: "POST",
            url: url,
            data: siteInfo,
            processData: false,
            contentType: false,
            success: function(data) {
                if (data.type == "success") {
                    alert(data.message);
                    $('#curDomain').html(data.data.domain);
                    var domainField = $('#domain');
                    $('form#companySite').reset();
                    domainField.focus();
                } else if (data.type == "error") {
                    $$.displayServerValidationResults(data)
                }
            },
            error: function() {
                alert("Something went wrong!")
            }
        })
    })

    $('#addTrailerBtn').on('click', function(e) {
        e.preventDefault();
        var form = $('#addTrailer'),
            url = form.attr('action'),
            trailer = form.serializeObject(),
            trailerFile = document.getElementById('trailer').files[0],
            fullTrailerInfo = new FormData();
        fullTrailerInfo.append('video', trailerFile);
        fullTrailerInfo.append('trailer', JSON.stringify(trailer));
        $.ajax({
            type: "POST",
            url: url,
            data: fullTrailerInfo,
            processData: false,
            contentType: false,
            success: function(data) {
                if (data.type == "error") {
                    $$.displayServerValidationResults(data)
                } else if (data.type == "success") {
                    if (data.data.focus) {
                        var options = [
                        data.data.id,
                        data.data.title,
                        data.data.length,
                        data.data.dtModify,
                        data.data.company,
                        '<a href="/company/trailers/remove/' + data.data.trailer_id + '/"><i class="icon-remove"></i></a>'
                        ];
                    } else {
                        var options = [
                        data.data.id,
                        data.data.title,
                        data.data.length,
                        data.data.dtModify,
                        '<a href="/company/trailers/remove/' + data.data.trailer_id + '/"><i class="icon-remove"></i></a>'
                        ];
                    }
                    /*var options = [
                        data.data.id,
                        data.data.title,
                        data.data.length,
                        data.data.dtModify,
                    ];*/
                    $('#companyTrailersTable').dataTable({
                        "bRetrieve": true
                    }).fnAddData(options);

                    $("#dialog_modal").attr('title', data.type);
                    $("#dialog_modal .error").text(data.message);
                    $("#dialog_modal").dialog({
                        autoOpen: false,
                        modal: true,
                        resizable: false,
                        draggable: false
                    }).find('button').click(function() {
                        $(this).parents('.ui-dialog-content').dialog('close');
                    });
                    $("#dialog_modal").dialog("open");
                }
            },
            error: function() {
                alert("FAIL!")
            }
        })
    });

    // Edit Trailer
    $(".editTrailerBtn").click(function() {
        var form = $('#editTrailer'),
            url = form.attr('action'),
            trailer = form.serializeObject();
        $.ajax({
            type: "POST",
            url: url,
            data: {
                mode: "edit",
                data: JSON.stringify(trailer)
            },
            success: function(data) {
                location.reload();
            }
        });
    });

    // Del Trailer
    $(".removeTrailerBtn").click(function() {
        if (confirm("Do you really want to delete?")) {
            var urlDelTrailerAjax = $(this).attr('href');
            console.log(urlDelTrailerAjax);
            $.ajax({
                type: "POST",
                url: urlDelTrailerAjax,
                data: {
                    mode: "remove"
                },
                dataType: "html",
                success: function(data) {
                    location.reload();
                }
            });
        return false;
        }
    });

    $('#defTrailerSchedule').on('click', function(e) {
        e.preventDefault();
        var domSchedule = $('#kioskTrailersSchedule').find('.scheduler .right select option'),
            schedule = domSchedule.map(function() {
                return this.getAttribute('data-id');
            }).toArray();

        $.ajax({
            type: "POST",
            data: {
                schedule: JSON.stringify(schedule)
            },
            dataType: "json",
            success: function(data) {
                if (data.type == "error") {
                    $$.displayServerValidationResults(data)
                } else if (data.type == "success") {
                    $("#dialog_modal").attr('title', data.type);
                    $("#dialog_modal .error").text(data.message);
                    $("#dialog_modal").dialog({
                        autoOpen: false,
                        modal: true,
                        resizable: false,
                        draggable: false
                    }).find('button').click(function() {
                        $(this).parents('.ui-dialog-content').dialog('close');
                    });
                    $("#dialog_modal").dialog("open");
                }
            },
            error: function() {
                alert("Error! Trailer can't be added")
            }
        })
    })

    // Scheduler
    $('.scheduler').each(function() {
        var target = $(this),
            leftSelect = target.find('.left select'),
            rightSelect = target.find('.right select'),
            addBtn = target.find('[data-id="add"]'),
            delBtn = target.find('[data-id="del"]'),
            upBtn = target.find('[data-id="up"]'),
            downBtn = target.find('[data-id="down"]'),
            addAllBtn = target.find('[data-id="add-all"]'),
            delAllBtn = target.find('[data-id="del-all"]'),
            filters = target.find('[data-id="filter"]');

        addBtn.on('click', function() {
            var selectedLeft = leftSelect.find('option:selected'),
                selectedRight = rightSelect.find('option:selected');

            if (selectedRight.length) {
                $(selectedRight).each(function() {
                    selectedLeft.clone().insertAfter($(this))
                })
            } else {
                rightSelect.append(selectedLeft.clone());
            }
        })

        delBtn.on('click', function() {
            var selectedRight = rightSelect.find('option:selected');
            selectedRight.remove();
        })

        upBtn.on('click', function() {
            var selectedRight = rightSelect.find('option:selected');
            selectedRight.each(function() {
                var target = $(this),
                    prev = target.prev();
                prev.before(target);
            })
        })

        downBtn.on('click', function() {
            var selectedRight = rightSelect.find('option:selected').reverse();
            selectedRight.each(function() {
                var target = $(this),
                    next = target.next();
                next.after(target);
            })
        })

        addAllBtn.on('click', function() {
            var Left = leftSelect.find('option'),
                Right = rightSelect.find('option');
            Right.each(function() {
                $(this).remove();
            })
            if (Right.length) {
                $(Right).each(function() {
                    Left.clone().insertAfter($(this))
                })
            } else {
                rightSelect.append(Left.clone());
            }
        })

        delAllBtn.on('click', function() {
            var Left = leftSelect.find('option'),
                Right = rightSelect.find('option');
            Right.each(function() {
                $(this).remove();
            })
        })

        filters.each(function() {
            var target = $(this),
                select = target.siblings('select');
            target.on('keyup', function(e) {
                select.children().show()
                select.children().filter(function() {
                    return !($(this).text().toLowerCase().indexOf(target.val().toLowerCase()) >= 0);
                }).hide();
            })
        })
    })

    // Company social communities
    $('#addCompanySocial').on('click', function(e) {
        e.preventDefault();
        var form = $('#companySocial'),
            community = form.serializeObject(),
            logo = document.getElementById('logo').files[0],
            communityInfo = new FormData();
        communityInfo.append('community', JSON.stringify(community));
        communityInfo.append('logo', logo);
        $.ajax({
            type: "POST",
            data: communityInfo,
            processData: false,
            contentType: false,
            success: function(data) {
                if (data.type == "error") {
                    $$.displayServerValidationResults(data)
                } else if (data.type == "success") {
                    var table = $('#companySocialTable'),
                        url = table.attr('data-remove-url').replace(0, data.data.socialId),
                        link = $('<a href="' + url + '"><i class="icon-remove"></i></a>'),
                        img = $('<img width="100" src="/media/company/' + data.data.companyId +
                            '/social/logos/' + data.data.logo + '"></img>');

                    if (data.data.focus) {
                       img = $('<img width="100" src="/media/company/' + data.data.company_id +
                            '/social/logos/' + data.data.logo + '"></img>');
                       var options = [
                            data.data.id,
                            data.data.brand,
                            data.data.url,
                            data.data.title,
                            img.wrap('<div>').parent().html(),
                            data.data.company,
                            link.wrap('<div>').parent().html()
                        ];
                    } else {
                        var options = [
                            data.data.id,
                            data.data.brand,
                            data.data.url,
                            data.data.title,
                            img.wrap('<div>').parent().html(),
                            link.wrap('<div>').parent().html()
                        ];
                    }



                    /*var options = [
                        data.data.id,
                        data.data.brand,
                        data.data.url,
                        data.data.title,
                        img.wrap('<div>').parent().html(),
                        link.wrap('<div>').parent().html()
                    ];*/

                    table.dataTable({
                        "bRetrieve": true
                    }).fnAddData(options);
                    $("#dialog_modal").attr('title', data.type);
                    $("#dialog_modal .error").text(data.message);
                    $("#dialog_modal").dialog({
                        autoOpen: false,
                        modal: true,
                        resizable: false,
                        draggable: false
                    }).find('button').click(function() {
                        $(this).parents('.ui-dialog-content').dialog('close');
                        form.find('input').val('')
                    });
                    $("#dialog_modal").dialog("open");
                }
            },
            error: function() {
                alert("FAIL!")
            }
        })
    })

    $('#movieSearch').live('keypress', function(e) {
        if (e.keyCode == 13) {
            var target = e.target,
                assign_url_pattern = target.getAttribute('data-assign-url');
            $.ajax({
                type: "GET",
                url: target.getAttribute('data-search-url'),
                data: {
                    'movie': target.value
                    // 'kioskId': target.getAttribute('data-kiosk-id') || undefined
                },
                dataType: 'json',
                success: function(data) {
                    var movies = data.results,
                        res = document.getElementById('popUpResults');
                    $('#popUpResults').empty();
                    for (var i = 0, len = movies.length; i < len; i++) {
                        url = assign_url_pattern.replace('100001', movies[i][3])
                        res.innerHTML +=
                            "<div class='tabled'><input data-assign-url={u} class='cell' type='radio' value='{upc}' \
                            name='upc'><label for='upc'>{m}</label></div>".supplant({
                                upc: movies[i][3],
                                m: movies[i].join('/'),
                                u: url
                            })
                    }
                },
                error: function() {
                    alert("FAIL!")
                }
            })
        }
    })

    $('#mapDiskToUpc').live('click', function(e) {
        var checkedRadio = $('#popUpResults input[type="radio"]:checked');
        $.ajax({
            type: "POST",
            url: checkedRadio.attr('data-assign-url'),
            success: function(data) {
                $('#unknownUpc').text(data.data.movieInfo);
                $("#dialog_modal").attr('title', data.type);
                $("#dialog_modal .error").text(data.message);
                $("#dialog_modal").dialog({
                    autoOpen: false,
                    modal: true,
                    resizable: false,
                    draggable: false
                }).find('button').click(function() {
                    $(this).parents('.ui-dialog-content').dialog('close');
                    form.find('input').val('')
                });
                $("#dialog_modal").dialog("open");
            },
            error: function() {
                alert("FAIL!")
            }
        })
    })

    $('.tooltip[data-id="clickTooltip"]').on('click', function(e) {
        e.stopPropagation();
        e.preventDefault();
        var $tooltip = $(e.target).closest('.tooltip'),
            grav = $tooltip.data('gravity') || $.fn.tipsy.autoNS,
            html = $tooltip.data('html') || false,
            anim = $tooltip.data('anim') || true;

        if ($tooltip.tipsy(true).options.trigger != 'manual') {
            $tooltip.attr('original-title', $tooltip.attr('click-title'));
            $tooltip.unbind('mouseenter');
            $tooltip.unbind('mouseleave');

            $tooltip.tipsy({
                gravity: grav,
                fade: anim,
                html: html,
                trigger: 'manual'
            });

            var tipsyObject = $tooltip.tipsy(true);
            tipsyObject.show();
            tipsyObject.$element.data('tipsy', tipsyObject);
            tipsyObject.$tip.data('tip', tipsyObject);
        }
    })

    $('i[data-id="closePopUp"]').live('click', function(e) {
        e.preventDefault();
        var $target = $(e.target),
            $tooltip = $target.closest('.tipsy').data('tip').$element,
            grav = $tooltip.data('gravity') || $.fn.tipsy.autoNS,
            html = $tooltip.data('html') || false,
            anim = $tooltip.data('anim') || true;

        $tooltip.attr('original-title', $tooltip.attr('hover-title'));
        $tooltip.data('tipsy').hide();

        $tooltip.tipsy({
            gravity: grav,
            fade: anim,
            html: html,
            trigger: 'hover'
        });
    });
    $('#order-date').click(function(){
        var href=$(this).attr('data-href');
        if($(this).prop('disabled')==false){
            $.ajax({
                type: "POST",
                url: href,
                data:"date",
                success: function(data) {
                    window.location=window.location.href.split('#')[0];
                },
                error: function() {
                    alert("FAIL!")
                }
            });
        }
    });
    $('#order-name').click(function(){
        var href=$(this).attr('data-href');
        if($(this).prop('disabled')==false){
            $.ajax({
                type: "POST",
                url: href,
                data:"name",
                success: function(data) {
                    window.location=window.location.href.split('#')[0];
                },
                error: function() {
                    alert("FAIL!")
                }
            });
        }
    });

    $('.review-inventory').click(function(){
        var href = $(this).attr('data-href');
        var review_type = $(this).attr('data-review-type');
        var data = [];

        if (review_type == 'slots'){
            $.each($('.slot-id:checked'), function(idx, val){
                data.push($(val).val());
            });
        }

        $.ajax({
            type: "POST",
            url: href,
            data: {slots: JSON.stringify(data)},
            success: function(data) {
                var close_function = null;
                if (data.type == 'success'){
                    close_function = function(){ window.location=window.location.href.split('#')[0]; };
                }
                $$.showModalMessage(data.type, data.message, close_function);
            },
            error: function() {
                alert("FAIL!")
            }
        });
    });

    $('.review-stop').click(function(){
        var href = $(this).attr('data-href');

        $.ajax({
            type: "POST",
            url: href,
            success: function(data) {
                $$.showModalMessage(data.type, data.message, function(){ window.location=window.location.href.split('#')[0]; });
            },
            error: function() {
                alert("FAIL!")
            }
        });
    });

    $('.disableKiosk').click(function(e){
        e.preventDefault();
         var href=$(this).attr('href');
         $.ajax({
            type: "POST",
            url: href,
            data:"date",
            success: function(data) {
                    window.location=window.location;
            },
            error: function() {
                alert("FAIL!")
            }
         });
    });

    $('#rentalFleetCompany').change(function(){
        $.ajax({
            type: "POST",
            url: $("#rentalFleetCompany").attr('data-tariff-plans-url'),
            data: {'company_id': $("#rentalFleetCompany :selected").val()},
            dataType: "json",
            success: function(data) {
                var searchSelect = document.querySelector('select#rentalFleetTariffPlanId');
                searchSelect.options.length = 0;
                searchSelect.appendChild(new Option('', ''));
                if (data.tariffPlans.length > 0) {
                    for (var i = 0, len = data.tariffPlans.length; i < len; i++) {
                        searchSelect.appendChild(new Option(data.tariffPlans[i].name, data.tariffPlans[i].id));
                        console.log(data.tariffPlans[i].id, data.tariffPlans[i].name);
                    }
                } else {
                    var noMatch = new Option('No tariff plans');
                    noMatch.disabled = true;
                    searchSelect.appendChild(noMatch);
                }
                $(searchSelect).trigger('chosen:updated');
            },
            error: function() {
                alert("Error during sending request!");
            }
        });
    });


    $('.add-to-eject-list').live('click',function(e){
        e.preventDefault();
        var then=$(this);
        var href=$(this).attr('href');
        $.ajax({
            type: "POST",
            url: href,
            data: 'add-to-eject-list',
            dataType: "json",
            success: function(data) {
                if(data.type=="success"){
                    if(data.type=="success"){
                       then.after(data.data.button);
                       then.parents('tr').find('.slot-status').text(data.data.status);
                       then.remove();
                        $$.registry.tooltips();
                        $('.tipsy').remove();
                    }
                }
            },
            error: function() {
                alert("Error during sending request!");
            }
        });
    });
    $('.remove-from-eject-list').live('click',function(e){
        e.preventDefault();
        var href=$(this).attr('href');
        var then=$(this);
        $.ajax({
            type: "POST",
            url: href,
            data: 'remove-from-eject-list',
            dataType: "json",
            success: function(data) {
                if(data.type=="success"){
                   then.after(data.data.button);
                   then.parents('tr').find('.slot-status').text(data.data.status);
                   then.remove();
                   $$.registry.tooltips();
                   $('.tipsy').remove();
                }
            },
            error: function() {
                alert("Error during sending request!");
            }
        });
    });
    /*$('.newtable').dataTable( {
        "aoColumnDefs": [
            { "asSorting": [ "asc" ], "aTargets": [ 0 ] }
        ]

    });
    */
    $('#sendBash').submit(function(e){
        e.preventDefault();
        var href=$('#butBash').attr('data-url');
        $('#butBash').attr('disabled','disabled');
        $.ajax({
            type: "POST",
            url: href,
            data: $('#command').val(),
            dataType: "json",
            success: function(data) {
                $('#butBash').removeAttr('disabled');
                if(data.type=="success"){
                    $('#command').val('');
                    var table = $('.newtable tbody');
                    if(data.data.dt_executed==undefined){
                        data.data.dt_executed="-";
                    }
                    if(data.data.exec_result==undefined){
                        data.data.exec_result='';
                    }
                    if($('.newtable tbody tr').length<10){

                    }
                    else{$('.newtable tbody tr:last-child').remove();}
                    table.prepend('<tr><td>'+ data.data.id+'</td><td>'+data.data.user_id+'</td><td>'+data.data.command+'</td><td>'+data.data.exec_result+'</td><td>'+data.data.dt_create+'</td><td>'+data.data.dt_executed+'</td></tr>');

                }
                if(data.type=="error"){

                }
            },
            error: function() {
                alert("Error during sending request!");
            }
        });
    });

    $('#sendCalibration').submit(function(e){
        if (confirm("You are changing kiosk calibration settings. This is very sensual data. Changing this may ruin proper robotics work. Do you really want to change it?")) {
            e.preventDefault();
            $('#butCalibration').attr('disabled', 'disabled');
            var href = $('#butCalibration').attr('data-url');
            var data = $('#sendCalibration').serializeObject();
            $.ajax({
                type: "POST",
                url: href,
                data: data,
                dataType: "json",
                success: function (data) {
                    $('#butCalibration').removeAttr('disabled');
                    if (data.type == "success") {

                    }
                    if (data.type == "error") {
                        $$.displayServerValidationResults(data);
                    }
                },
                error: function () {
                    alert("Error during sending request!");
                }
            });
        }
    });


});