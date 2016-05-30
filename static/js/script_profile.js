// ! Your application

(function($, window, document, undefined) {

    $('#btn-save').click(function(event) {
        event.preventDefault();
        form = $('#personal_data').find('form:visible');
        $.ajax({
            type: form.attr('method'),
            url: form.attr('action') + form.attr('name'),
            data: form.serialize(),
            dataType: 'json'
        })
            .done(function(response) {
                location.reload();
                return true
            });
    });

    $('#btn-change-password').click(function(event) {
        event.preventDefault();
        form = $('#settings_password');
        $.ajax({
            type: form.attr('method'),
            url: form.attr('action'),
            data: form.serialize(),
            dataType: "json"
        })
            .done(function(response) {
                $msg = $('.pass-messages');
                if (response.error) {
                    $msg.find('.failure').text(response.message);
                    $msg.find('.failure').fadeIn();
                    form.find("input").val("");
                    form.find("input").addClass("error");
                    form.find("input").removeClass("valid");
                    return false
                }
                return true
            });
    });

})(jQuery, this, document);