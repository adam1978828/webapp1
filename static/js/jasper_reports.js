$(document).ready(function () {
    initDatePickers();

    function initDatePickers() {
        $.datepicker._defaults.dateFormat="dd.mm.yy";

        $.each($('.default-date-picker'), function(idx, val){
            var dt_val = $(val).val();
            console.log(dt_val);
            $(val).datepicker().datepicker('option', 'dateFormat', $(val).attr('date-format'));
            $(val).datepicker().datepicker('option', 'changeMonth', true);
            $(val).datepicker().datepicker('option', 'changeYear', true);
            $(val).datepicker().datepicker('setDate', dt_val);
        });

        $.each($('.default-date-picker2'), function(idx, val){
            $(val).datetimepicker('option', 'dateFormat', $(val).attr('date-format'));
        });
    }

    $('#getJasperReportParams').click(function(event){
        event.preventDefault();

        $.ajax({
            type: 'POST',
            url: $(this).attr('data-url'),
            dataType: 'json',
            data: {alias: $('#jasperReports').val()},
            success: function (data) {
                if (data.type == 'success') {
                    $('#reportContent').html(data.content);
                    $$.utils.forms.resize();
                    initDatePickers();
                } else{
                    $$.showModalMessage(data.type, data.message, null);
                }
            }
        });
    });

    $('#reportContent').on('click', '#jasperBuildButton',function(event){
        event.preventDefault();
        var data = $('#jasperReportParams').serializeObject();

        $.ajax({
            type: 'POST',
            url: $(this).attr('data-url'),
            dataType: 'json',
            data: {data: JSON.stringify(data)},
            success: function (data) {
                if (data.type == 'success') {
                    $('#htmlReportContent').html(data.content);
                    $$.utils.forms.resize();
                    initDatePickers();
                } else{
                    $$.showModalMessage(data.type, data.message, null);
                }
            }
        });
    });


    $('#saveJasperTemplate').click(function(event){
        event.preventDefault();

        $.ajax({
            type: 'POST',
            url: $(this).attr('data-url'),
            dataType: 'json',
            data: {data: JSON.stringify($('#jasperTemplateForm').serializeObject())},
            success: function (data) {
                if (data.type == 'success') {
                    $$.showModalMessage(data.type, data.message, function(){
                        window.location = data.redirect_url;
                    });
                } else{
                    $$.showModalMessage(data.type, data.message, null);
                }
            }
        });
    });

    $('.removeJasperTemplate').click(function (e) {

        e.preventDefault();
        var dataId = $(this).attr('data-id');
        var dataName = $(this).attr('data-name');
        var url = $(this).attr('href');
        $("#dialog-confirm").attr('title', 'Confirm');
        $("#dialog-confirm .error").text('Remove jasper template '+dataName+'?');
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
                        $('#jasper-template-table').find('tr').each(function () {
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
});