$(document).ready(function () {
    var refreshUrl = $('#urlRefreshUpdateCenter').val();
    var refreshTimer = null;
    var refreshBlockTimer = null;
    var refreshTimerBlock = $('#autoRefreshInBlock');
    var refreshTimeOut = 10;

    if ($('#needRefreshUpdateCenter').val() == 1){
        runRefresh();
    }

    function runRefresh(){
        if (refreshTimer != null){
            clearInterval(refreshTimer);
        }

        if (refreshBlockTimer != null){
            clearInterval(refreshBlockTimer);
        }

        refreshTimeOut = 10;
        refreshTimer = setInterval(refreshUpdateCenter, 11000);
        refreshBlockTimer = setInterval(refreshBlock, 1000);
        refreshTimerBlock.removeClass('hidden');
    }

    function stopRefresh(){
        clearInterval(refreshTimer);
        clearInterval(refreshBlockTimer);
    }

    function refreshBlock(){
        $('#autoRefreshIn').html(refreshTimeOut);
        refreshTimeOut -= 1;
    }

    function refreshUpdateCenter(){
        stopRefresh();
        $.ajax({
            type: 'POST',
            url: refreshUrl,
            dataType: 'json',
            data: null,
            success: function (data) {
                if (data.finalized){
                    refreshTimerBlock.addClass('hidden');
                    $('#updateMoviesLogTable').dataTable().fnDraw();
                    $('#moviesUpdateAlt').prop('disabled', false);
                    $('#moviesPosterHashUpdateAlt').prop('disabled', false);
                }else{
                    runRefresh();
                }

                var stats = $('#updateStats').find('.value');
                $(stats[0]).html(data.start_dt);
                $(stats[1]).html(data.status);
                $(stats[2]).html(data.detected);
                $(stats[3]).html(data.exists);
                $(stats[4]).html(data.not_recognized);
                $(stats[5]).html(data.saved);
                $(stats[6]).html(data.hash_handled);
            }
        });
    }

    $('#moviesUpdateAlt, #moviesPosterHashUpdateAlt').click(function(event){
        event.preventDefault();

        if (!$(this).prop('disabled')) {
            $(this).prop('disabled', true);
        }

        $.ajax({
            type: 'POST',
            url: $(this).attr('data-url'),
            dataType: 'json',
            data: null,
            success: function (data) {
                var close_function = null;

                if (data.type == 'success') {
                    close_function = function(){
                        $(this).parents('.ui-dialog-content').dialog('close');
                        runRefresh();
                        $('#updateMoviesLogTable').dataTable().fnDraw();
                    };
                }

                $$.showModalMessage(data.type, data.message, close_function);
            }
        });
    });
});