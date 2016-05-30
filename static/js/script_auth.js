// ! Your application

$(document).ready(function(){
    $('#restore_password_form').submit(function(event){
        event.preventDefault();
            var form = $(this);
            if(form.find('#email').next().hasClass('icon valid-icon')){
                $.ajax({
                    type: $(form).attr('method'),
                    url: $(form).attr('action'),
                    data: $(form).serialize(),
                    dataType : 'json',
                    success:function (response) {
                        if (response.error) {
                            $login = $('#login');
                            $msg = $login.find('.restore-messages');
                            if (response.error) {
                                $msg.find('.failure').text(response.message);
                                $msg.find('.welcome').fadeOut();
                                $msg.find('.failure').fadeIn();
                            } else {
                                $msg.find('.welcome').text('Please, check your email and follow the link');
                                $msg.find('.failure').fadeOut();
                                $msg.find('.welcome').fadeIn();
                                $login.find('.form-box').fadeOut();
                                $login.find('.actions').fadeOut();
                            }
                        }
                    }
                });
            }
    });
    $('#new_password_form').submit(function(event){
        event.preventDefault();
            var form = $(this);
            if(form.find('#v1_repeat_password').next().hasClass('icon valid-icon')){
                $.ajax({
                    type: $(form).attr('method'),
                    url: $(form).attr('action'),
                    data: $(form).serialize(),
                    dataType : 'json',
                    success:function (response) {
                            $login = $('#login');
                            $msg = $login.find('.login-messages');
                            if (response.error) {
                                $msg.find('.failure').text(response.message);
                                $msg.find('.welcome').fadeOut();
                                $msg.find('.failure').fadeIn();
                            } else {
                               $msg.find('.welcome').text('Your password is successfully changed. You can login now.');
                                $msg.find('.failure').fadeOut();
                                $msg.find('.welcome').fadeIn();
                                $login.find('.form-box').fadeOut();
                                $login.find('.actions').fadeOut();
                                $login.find('#login_div').fadeIn();
                            }
                        }
                });
            }
    });
    $('#login_form').submit(function(event){
        event.preventDefault();
            var form = $(this);
            var method = $(form).attr('method');
            var url= $(form).attr('action');
            if(form.find('#login_name').next().hasClass('icon valid-icon') && form.find('#login_pw').next().hasClass('icon valid-icon')){
                $.ajax({
                    type: $(form).attr('method'),
                    url: $(form).attr('action'),
                    data: $(form).serialize(),
                    dataType : 'json',
                    success:function (response) {
                        if (response.error) {
                            $login = $('#login');
                            $msg = $login.find('.login-messages');
                            $msg.find('.failure').text('Invalid email or password');
                            $msg.find('.welcome').fadeOut();
                            $msg.find('.failure').fadeIn();
                            $(form).find('#login_name').addClass('error');
                            $(form).find('#login_pw').addClass('error');
                            $(form).find('#login_name').removeClass('valid');
                            $(form).find('#login_pw').removeClass('valid');
                        } else {
                            window.location.href = response.next;
                        }
                    }
                });
            }
    });
});


(function($, window, document, undefined){

	// Put all JS you need in addition to script.js here

//    $('#login_form').validationOptions({
//            submitHandler: function(){alert('Hello')}
//    });
//
//    $("#login_form").validate({
//        rules: {
//            login_pw: {
//                required: true,
//                email: true,
//                check_credentials: true
//    }}});

})(jQuery, this, document);
