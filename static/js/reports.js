$(document).ready(function () {
    if($('#filters').length>0){
        $.datepicker._defaults.dateFormat="dd.mm.yy";
        $('#filters .default-date-picker').datepicker();
        $('#filters .default-date-picker2').datetimepicker();
    }
    var fieldsTable = $('#fields');
    var ordersTable = $('#order_by_fields');
    var aggsTable = $('#aggregations');
    var groupByTable = $('#group_by_fields');
    var filtersTable = $('#filters');
    var subFieldsTable = $('#subFieldsTable');
    var blankFieldWrapper = $('#blankFieldWrapper');
    var notBlankFieldWrapper = $('#notBlankFieldWrapper');
    var removeotchet = $('.removeOtchet');
    var removeshablon = $('.removeShablon');

    var sortableOptions = { axis: "y", forcePlaceholderSize: true, tolerance: "pointer" };

    $("#fields .rep-sortable").not('.sub-fields .rep-sortable').sortable();
    $("#filters tbody").sortable(sortableOptions);
    $("#order_by_fields tbody").sortable(sortableOptions);
    $("#aggregations tbody").sortable(sortableOptions);
    $("#group_by_fields tbody").sortable(sortableOptions);
    $('#ds-fields-sortable').sortable(sortableOptions);
    $('.sub-sorted').sortable(sortableOptions);

    $('.removeShablon').click(function (e) {
        e.preventDefault();
       var dataId = $(this).attr('data-id');
        var dataName = $(this).attr('data-name');
        var url = $(this).attr('href');
        $("#dialog-confirm").attr('title', 'Confirm');
        $("#dialog-confirm .error").text('Remove pattern '+dataName+'?');
        $("#dialog-confirm").dialog({
            autoOpen: false,
            modal: true,
            resizable: false,
            draggable: false,
            show: null,
            hide: null
        }).find('button').off('click').on('click',function() {
            $(this).parents('.ui-dialog-content').dialog('close');
            if($(this).attr('id')=='delok'){
                $.ajax({
                    type: 'POST',
                    url: url,
                    data: {id: dataId},
                    success: function (data) {
                        if (data.type == "success") {
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
                            });
                            $("#dialog_modal").dialog("open");
                            $('#report-pattern-table').find('tr').each(function () {
                                if ($(this).attr('data-id') == dataId) {
                                    $(this).remove();
                                }
                            });
                        }
                    }
                });
            }
        });
        $("#dialog-confirm").dialog("open");
    });
    $('.removeOtchet').click(function (e) {

        e.preventDefault();
        var dataId = $(this).attr('data-id');
        var dataName = $(this).attr('data-name');
        var url = $(this).attr('href');
        $("#dialog-confirm").attr('title', 'Confirm');
        $("#dialog-confirm .error").text('Remove report '+dataName+'?');
        $("#dialog-confirm").dialog({
            autoOpen: false,
            modal: true,
            resizable: false,
            draggable: false,
            show: null,
            hide: null
        }).find('button').off('click').on('click',function() {
            $(this).parents('.ui-dialog-content').dialog('close');
            if($(this).attr('id')=='delok'){
                $.ajax({
                    type: 'POST',
                    url: url,
                    data: {id: dataId},
                    success: function (data) {
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
                        });
                        $("#dialog_modal").dialog("open");
                        $('#report-table').find('tr').each(function () {
                            if ($(this).attr('data-id') == dataId) {
                                $(this).remove();
                            }
                        });
                    }
                });
            }
        });
        $("#dialog-confirm").dialog("open");
    });
    $('#createReportPattern').click(function (event) {
        event.preventDefault();
        window.location = $('#reportPatterns').val();
    });

    $('#createReport').click(function (event) {
        event.preventDefault();
        window.location = $('#customReportPatterns').val();
    });

    $('#addRootField').click(function (event) {
        event.preventDefault();

        var fieldsList = $(this).parent().parent().find('.fields-set')[0];

        var alias = $(fieldsList).val();
        var name = $(fieldsList).find('option:selected').html().trim();
        var fieldBlock;

        if (alias == '') {
            fieldBlock = $(blankFieldWrapper.clone());
        }
        else {
            fieldBlock = $(notBlankFieldWrapper.clone());
        }

        fieldBlock.removeAttr('id');

        var readableName = fieldBlock.find('input[name=readable_name]');
        $(readableName).val(name);

        var fieldAlias = fieldBlock.find('input[name=alias]');
        $(fieldAlias).val(alias);
        var my = $('<td><i class="icon icon-sort"></i></td>');
        var elem = $('<tr></tr>').append($('<td><div class="sub-sorted"></div></td>').prepend(fieldBlock));
        elem.prepend(my);
        elem.find('select').next().remove();
        fieldsTable.append($(elem));
        $('.sub-sorted').sortable(sortableOptions);
        $('#fields').find('select').each(function(i, v) {
            $(v).chosen({disable_search: true});
        });

    });

    $('#fields').on('click', '.add-field', function (event) {
        event.preventDefault();

        var fieldsList = $(this).parent().find('.fields-set')[0];

        var alias = $(fieldsList).val();
        var name = $(fieldsList).find('option:selected').html().trim();
        var fieldBlock;

        if (alias == '') {
            fieldBlock = $(blankFieldWrapper.clone());
        }
        else {
            fieldBlock = $(notBlankFieldWrapper.clone());
        }

        fieldBlock.removeAttr('id');

        var readableName = fieldBlock.find('input[name=readable_name]');
        $(readableName).val(name);

        var fieldAlias = fieldBlock.find('input[name=alias]');
        $(fieldAlias).val(alias);

        var tmpFieldTable = $(subFieldsTable.clone());
        tmpFieldTable.removeAttr('id');

        var my = $('<td><i class="icon icon-sort"></i></td>');
        var elem = $('<tr></tr>').append($('<td><div class="sub-sorted"></div></td>').prepend(fieldBlock));

        elem.prepend(my);
        tmpFieldTable.append($(elem));

        elem = $('<div class="sub-fields grid_12"></div>').append(tmpFieldTable);
        elem.find('select').next().remove();
        var sub_block = $(this).parent().next();
        if (sub_block.length != 0) {
            $(sub_block[0]).append(elem);
        }
        else {
            elem.insertAfter($(this).parent());
        }

        $('.sub-sorted').sortable(sortableOptions);

        $('#fields').find('select').each(function(i, v) {
            $(v).chosen({disable_search: true});
        });
    });

    $('#fields').on('click', '.remove-field', function (event) {
        event.preventDefault();

        var elem = $(this).parents('tr');
        var sub = $(this).parents('div.sub-fields');

        $(elem[0]).remove();
        $(sub[0]).remove();
    });

    $('#addOrdering').click(function (event) {
        event.preventDefault();

        var ordersList = $(this).parent().parent().find('#orders-set')[0];
        var option = $(ordersList).find('option:selected');
        var alias = $(ordersList).val();
        var orderBlock = $('.orders-set').find('.order-by-' + alias);

        orderBlock = $(orderBlock).clone();
        var my = $('<td><i class="icon icon-sort"></i></td>');
        var elem = $('<tr></tr>').append($('<td></td>').append(orderBlock));
        elem.prepend(my);

        elem.find('select').next().remove();
        ordersTable.append($(elem));

        option = $(option);
        option.attr('hidden', '');
        option.removeAttr('selected');
        $('#order_by_fields').find('select').each(function(i, v) {
            $(v).chosen({disable_search: true});
        });
    });

    $('#order_by_fields').on('click', '.remove-order', function (event) {
        event.preventDefault();

        var elem = $(this).parent().parent().parent();
        var alias = $(elem).find('input[name=alias]').val();

        var op = $('#orders-set').find('option[value=' + alias + ']');
        op.removeAttr('hidden');

        elem.remove();
    });

    $('#addAggregation').click(function (event) {
        event.preventDefault();

        var aggList = $(this).parent().parent().find('#aggregations-set')[0];
        var option = $(aggList).find('option:selected');
        var alias = $(aggList).val();
        var aggBlock = $('.aggregations-set').find('.agg-by-' + alias);

        aggBlock = $(aggBlock).clone();
        var my = $('<td><i class="icon icon-sort"></i></td>');
        var elem = $('<tr></tr>').append($('<td></td>').append($(aggBlock)));
        elem.prepend(my);
        elem.find('select').next().remove();
        aggsTable.append($(elem));
        $('#aggregations').find('select').each(function(i, v) {
            $(v).chosen({disable_search: true});
        });
        //option = $(option);
        //option.attr('hidden', '');
        //option.removeAttr('selected');
    });

    $('#aggregations').on('click', '.remove-agg', function (event) {
        event.preventDefault();

        var elem = $(this).parent().parent().parent();
        var alias = $(elem).find('input[name=alias]').val();

        var op = $('#aggregations-set').find('option[value=' + alias + ']');
        op.removeAttr('hidden');

        elem.remove();
    });

    $('#addGrouping').click(function (event) {
        event.preventDefault();

        var groupList = $(this).parent().parent().find('#grouping-set')[0];
        var option = $(groupList).find('option:selected');
        var alias = $(groupList).val();
        var groupBlock = $('.grouping-set').find('.group-by-' + alias);

        groupBlock = $(groupBlock).clone();
        var my = $('<td><i class="icon icon-sort"></i></td>');
        var elem = $('<tr></tr>').append($('<td></td>').append($(groupBlock)));
        elem.prepend(my);
        groupByTable.append($(elem));

        option = $(option);
        option.attr('hidden', '');
        option.removeAttr('selected');
    });

    $('#group_by_fields').on('click', '.remove-group', function (event) {
        event.preventDefault();

        var elem = $(this).parent().parent().parent();
        var alias = $(elem).find('input[name=alias]').val();

        var op = $('#grouping-set').find('option[value=' + alias + ']');
        op.removeAttr('hidden');

        elem.remove();
    });

    $('#addFilter').click(function (event) {
        event.preventDefault();
        var filterList = $(this).parent().parent().parent().find('#filters-set')[0];
        var option = $(filterList).find('option:selected');
        var alias = $(filterList).val();
        var filterBlock = $('.filters-set').find('.filter-by-' + alias);
            filterBlock = $(filterBlock).clone();
        var my = $('<td><i class="icon icon-sort"></i></td>');
        var elem = $('<tr></tr>').append($('<td></td>').append($(filterBlock)));
        elem.prepend(my);
        elem.find('select').next().remove();
        filtersTable.append($(elem));
        //option = $(option);
        //option.attr('hidden', '');
        //option.removeAttr('selected');
        $('#filters').find('select').each(function(i, v) {
            $(v).chosen({disable_search: true});
        });

        $('#filters .default-date-picker').datepicker();
        $('#filters .default-date-picker2').datetimepicker();

    });

    $('#filters').on('click', '.remove-filter', function (event) {
        event.preventDefault();

        var elem = $(this).parent().parent().parent();
        var alias = $(elem).find('input[name=alias]').val();

        var op = $('#grouping-set').find('option[value=' + alias + ']');
        op.removeAttr('hidden');

        elem.remove();
    });

    $('.save-pattern').click(function (event) {
        event.preventDefault();
        var rep = serializeReport();
        var url=$(this).attr('href');
        var dataUrl=$(this).attr('data-url');
        $.ajax({
            type: 'POST',
            url: url,
            dataType: 'json',
            data: {data: JSON.stringify(rep)},
            success: function (data) {

                if (data.type == 'error') {
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
                    });
                    $("#dialog_modal").dialog("open");
                }

                if (data.type == 'success') {
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
                        window.location = dataUrl+data.id;
                    });
                    $("#dialog_modal").dialog("open");
                }
            }
        });
    });
    $('.save-report').click(function (event) {
        event.preventDefault();
        var rep = serializeReport();
         var url=$(this).attr('href');
        var dataUrl=$(this).attr('data-url');
        $.ajax({
            type: 'POST',
            url: url,
            dataType: 'json',
            data: {data: JSON.stringify(rep)},
            success: function (data) {
                if (data.type == 'error') {
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
                    });
                    $("#dialog_modal").dialog("open");
                }
                if (data.type == 'success') {

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
                        window.location = dataUrl+data.id;
                    });
                    $("#dialog_modal").dialog("open");
                }
            }
        });
    });

    $('.save-existing-pattern').click(function (event) {
        event.preventDefault();
        var rep = serializeReport();
        var url=$(this).attr('href');
        $.ajax({
            type: 'POST',
            url: url,
            dataType: 'json',
            data: {data: JSON.stringify(rep)},
            success: function (data) {
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
                    });
                    $("#dialog_modal").dialog("open");
            }
        });
    });

    $('.build-report').click(function (event) {
        event.preventDefault();
        var rep = serializeReport();
        var url=$(this).attr('href');
        $.ajax({
            type: 'POST',
            url: url,
            dataType: 'json',
            data: {data: JSON.stringify(rep)},
            success: function (data) {
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
                    });
                    $("#dialog_modal").dialog("open");

                if (data.type == 'success') {
                    $('#repContent').html(data.content);
                }
            }
        });
    });

    function serializeReport() {
        var report = {};

        var repGeneral = $('#repGeneral');
        report.report_id = repGeneral.find('input[name=report_id]').val();
        report.pattern_id = repGeneral.find('input[name=pattern_id]').val();
        report.header = repGeneral.find('input[name=header]').val();
        report.is_available_for = repGeneral.find('select[name=is_available_for]').val();
        report.alias = repGeneral.find('input[name=alias]').val();

        var repFilters = $('#filters');
        var filters = repFilters.find('.rep-filter');

        report.filters = [];

        $.each(filters, function (idx, val) {
            var tmpFilter = {};
            var obj = $(val);

            tmpFilter.alias = obj.find('input[name=alias]').val();
            tmpFilter.op_alias = obj.find('select[name=op_alias]').val();
            tmpFilter.is_final = obj.find('select[name=is_final]').val();

            if (obj.find('input[name=data]').length == 0) {
                tmpFilter.data = obj.find('select[name=data]').val();
            }
            else {
                tmpFilter.data = obj.find('input[name=data]').val();
            }

            report.filters.push(tmpFilter);
        });

        report.filter_operation = $('#repFilters').find('select[name=filter_operation]').val();

        var repAggregations = $('#aggregations');
        var aggregations = repAggregations.find('.rep-aggregation');

        report.aggregations = [];

        $.each(aggregations, function (idx, val) {
            var tmpAgg = {};
            var obj = $(val);

            tmpAgg.alias = obj.find('input[name=alias]').val();
            tmpAgg.agg_alias = obj.find('select[name=agg_alias]').val();
            tmpAgg.header = obj.find('input[name=header]').val();

            report.aggregations.push(tmpAgg);
        });

        var regGroupBy = $('#group_by_fields');
        var group_by_fields = regGroupBy.find('.rep-group-by');

        report.group_by_fields = [];

        $.each(group_by_fields, function (idx, val) {
            report.group_by_fields.push($(val).find('input[name=alias]').val());
        });

        var repOrderBy = $('#order_by_fields');
        var order_by_fields = repOrderBy.find('.rep-order-by');

        report.order_by_fields = [];

        $.each(order_by_fields, function (idx, val) {
            var tmpOrder = {};
            var obj = $(val);

            tmpOrder.alias = obj.find('input[name=alias]').val();
            tmpOrder.order = obj.find('select[name=order]').val();

            report.order_by_fields.push(tmpOrder);
        });

        var fields = $('#fields>tbody>tr>td:nth-child(2)');

        report.fields = [];

        $.each(fields, function (idx, val) {
            report.fields.push(serialzeField($(val)));
        });

        return report;
    }

    function serialzeField(obj) {
        var result = {};

        var field = $(obj).children('.field-wrapper');

        result.alias = field.find('input[name=alias]').val();
        result.header = field.find('input[name=header]').val();
        result.sub_fields = [];

        var subFields = $(obj).children('.sub-sorted').children('.sub-fields');

        $.each(subFields, function (idx, val) {
            var tmp = $(val).find('table>tbody>tr>td:nth-child(2)')[0];
            result.sub_fields.push(serialzeField($(tmp)));
        });

        return result;
    }

    $('#save-ds').click(function (event) {
        event.preventDefault();
        var data = {};
        data.fields = [];

        $.each($('.ds_settings'), function (idx, val) {
            data.fields.push($(val).serializeObject());
        });

        data.fields_order = $('#ds-fields').serializeObject();
        var url = $(this).attr('href');
        $.ajax({
            type: 'POST',
            url: url,
            dataType: 'json',
            data: {data: JSON.stringify(data)},
            success: function (data) {
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
                    });
                    $("#dialog_modal").dialog("open");
            }
        });
    });

    $('.ds-setup-field').click(function(event){
        event.preventDefault();
        $('form.ds_settings').hide();
        $('form[alias="' + $(this).attr('alias') + '"]').show();
        $$.utils.forms.resize();
    });
});