"use strict";

//Plaeholder handler
$(function() {
    if (!Modernizr.input.placeholder) { //placeholder for old brousers and IE
        $('[placeholder]').focus(function() {
            var input = $(this);
            if (input.val() == input.attr('placeholder')) {
                input.val('');
                input.removeClass('placeholder');
            }
        }).blur(function() {
            var input = $(this);
            if (input.val() == '' || input.val() == input.attr('placeholder')) {
                input.addClass('placeholder');
                input.val(input.attr('placeholder'));
            }
        }).blur();
        $('[placeholder]').parents('form').submit(function() {
            $(this).find('[placeholder]').each(function() {
                var input = $(this);
                if (input.val() == input.attr('placeholder')) {
                    input.val('');
                }
            })
        });
    }

    $('#contact-form').submit(function(e) {
        e.preventDefault();
        var error = 0;
        var self = $(this);
        var $name = self.find('[name=user-name]');
        var $email = self.find('[type=email]');
        var $message = self.find('[name=user-message]');
        var emailRegex = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/;
        if (!emailRegex.test($email.val())) {
            createErrTult('Error! Wrong email!', $email)
            error++;
        }
        if ($name.val().length > 1 && $name.val() != $name.attr('placeholder')) {
            $name.removeClass('invalid_field');
        } else {
            createErrTult('Error! Write your name!', $name)
            error++;
        }
        if ($message.val().length > 2 && $message.val() != $message.attr('placeholder')) {
            $message.removeClass('invalid_field');
        } else {
            createErrTult('Error! Write message!', $message)
            error++;
        }
        if (error != 0) return;
        self.find('[type=submit]').attr('disabled', 'disabled');
        self.children().fadeOut(300, function() {
            $(this).remove()
        })
        $('<p class="success"><span class="success-huge">Thank you!</span> <br> your message successfully sent</p>').appendTo(self).hide().delay(300).fadeIn();
        var formInput = self.serialize();
        $.post(self.attr('action'), formInput, function(data) {}); // end post
    }); // end submit

    $('.btn-add-cart').click(function(e) {
        e.preventDefault();
        var self = $(this);
        var urlAdd = self.attr('href');
        var dataToken = self.parent().find('input[name=csrfmiddlewaretoken]').val();
        var formatId = self.attr('data-id');
        var movieId = self.attr('data-movie');
        $.ajax({
            type: "POST",
            url: urlAdd,
            data: {
                'csrfmiddlewaretoken': dataToken,
                'formatId': formatId
            },
            success: function(data) {
                $('#normal-kioskselect').show();
                $('#success-kioskselect').hide();
                $('#selectKiosk').remove();
                $(data).prependTo($('#add-cart-form').children('#normal-kioskselect'));
                $('.kioskselect').addClass('open');
                $(".select__sort").selectbox({
                    onChange: function(val, inst) {
                        $(inst.input[0]).children().each(function(item) {
                            $(this).removeAttr('selected');
                        })
                        $(inst.input[0]).find('[value="' + val + '"]').attr('selected', 'selected');
                    }
                });
                $('#movieId').val(movieId);
                $('#formatId').val(formatId);
            },
            error: function() {
                alert_fail();
            }
        });
    });
    $('.btn-add-cart-pref').click(function(e) {
        e.preventDefault();
        var self = $(this);
        var formatId = self.attr('data-id');
        var movieId = self.attr('data-movie');
        var url = self.attr('href');
        var carthref = $('.fa-shopping-cart').attr('href');
        var dataToken = self.parent().find('input[name=csrfmiddlewaretoken]').val();
        var colCart = $('.col-cart').text();
        $.ajax({
            type: "POST",
            url: url,
            data: {
                'csrfmiddlewaretoken': dataToken,
                'movieId': movieId,
                'formatId': formatId
            },
            success: function(data) {
                if (data.type == "error") {
                    $('.alertmodal').addClass('open');
                    $('.alertmodal .login-edition').text(data.message);
                }

                if (data.type == "info") {
                    $('#normal-kioskselect').show();
                    $('#success-kioskselect').hide();
                    $('#selectKiosk').remove();
                    $(data.data.partial).prependTo($('#add-cart-form').children('#normal-kioskselect'));
                    $('.kioskselect').addClass('open');
                    $(".select__sort").selectbox({
                        onChange: function(val, inst) {
                            $(inst.input[0]).children().each(function(item) {
                                $(this).removeAttr('selected');
                            })
                            $(inst.input[0]).find('[value="' + val + '"]').attr('selected', 'selected');
                        }
                    });
                    $('#movieId').val(movieId);
                    $('#formatId').val(formatId);
                    $('.choosekiosk').text('Available in:')
                }

                if (data.type == "success") {
                    if (data.data.template != undefined) {
                        $('#normal-kioskselect').show();
                        $('#success-kioskselect').hide();
                        $('#selectKiosk').remove();
                        $(data.data.template).prependTo($('#add-cart-form').children('#normal-kioskselect'));
                        $('.kioskselect').addClass('open');
                        $(".select__sort").selectbox({
                            onChange: function(val, inst) {
                                $(inst.input[0]).children().each(function(item) {
                                    $(this).removeAttr('selected');
                                })
                                $(inst.input[0]).find('[value="' + val + '"]').attr('selected', 'selected');
                            }
                        });
                        $('#movieId').val(movieId);
                        $('#formatId').val(formatId);
                    } else {
                        $('.kioskselect').addClass('open');
                        $('#normal-kioskselect').hide();
                        $('#success-kioskselect').show();
                        $('.btn-add-cart-pref').each(function() {
                            if ($(this).attr('data-movie') == movieId && $(this).attr('data-id') == formatId) {
                                $(this).hide();
                                $(this).next().show();
                                $(this).unbind('click');
                            }
                        });
                        $('.col-cart').text(data.data.disks_amount);
                    }
                }
                if (data.type == "warning") {
                    $('.alertmodal').addClass('open');
                    $('.alertmodal .login-edition').text(data.message);
                }
            },
            error: function() {
                alert_fail();
            }
        });
    });


    $('#add-cart-form').submit(function(e) {
        e.preventDefault();
        var self = $(this);
        self.find('[type=submit]').attr('disabled', 'disabled');
        var url = self.attr('action');
        var movieId = self.find('#movieId').val();
        var formatId = self.find('#formatId').val();
        var carthref = $('.fa-shopping-cart').attr('href');
        var reservationfield = self.serialize();
        var colCart = $('.col-cart').text();
        $.ajax({
            type: "POST",
            url: url,
            data: reservationfield,
            success: function(data) {
                self.find('[type=submit]').removeAttr('disabled');
                if (data.type == "error") {} else if (data.type == "success") {
                    $('#normal-kioskselect').hide();
                    $('#success-kioskselect').show();
                    $('.btn-add-cart-pref').each(function() {
                        if ($(this).attr('data-movie') == movieId && $(this).attr('data-id') == formatId) {
                            $(this).hide();
                            $(this).next().show();
                            $(this).unbind('click');
                        }
                    });
                    $('.col-cart').text(data.data.disks_amount);
                    $('.choose').text(data.data.name);
                    if (data.data.partial) {
                        $('#movies').html(data.data.partial)
                    }
                }
            },
            error: function() {
                alert_fail();
            }
        });
    });
    $('#login-form').submit(function(e) {
        e.preventDefault();
        var error = 0;
        var self = $(this);
        self.find('[type=submit]').attr('disabled', 'disabled');
        var $email = self.find('[type=email]');
        var $pass = self.find('[type=password]');
        var emailRegex = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/;
        if (!emailRegex.test($email.val())) {
            //createErrTult("Error! Wrong email!", $email)
            //error++;
        }
        if ($pass.val().length > 1 && $pass.val() != $pass.attr('placeholder')) {
            //$pass.removeClass('invalid_field');
        } else {
            //createErrTult('Error! Wrong password!', $pass)
            //error++;
        }
        var url = self.attr('action');
        var loginfield = self.serialize();
        $.ajax({
            type: "POST",
            url: url,
            data: loginfield,
            success: function(data) {
                self.find('[type=submit]').removeAttr('disabled');
                if (data.type == "error") {
                    for (var i = 0; i < data.errors.length; i++) {
                        self.find('input').each(function(index) {
                            if ($(this).attr('name') == data.errors[i].field) {
                                createErrTult(data.errors[i].message, $(this));
                            }
                        });
                    }
                } else if (data.type == "success") {
                    window.location = window.location;
                } else if (data.type == "info") {
                    var mail = data.data.send_email_again;
                    if (mail) {
                        $("#emailSignupo").val(mail);
                        changeWindow('signupo');
                    }
                }
            },
            error: function() {
                alert_fail();
            }
        });
        /*
		if (error!=0)return;
		self.find('[type=submit]').attr('disabled', 'disabled');
        var url=self.attr('action');
        var loginfield=self.serialize();
        $.ajax({
            type: "POST",
            url: url,
            data: loginfield,
            success: function(data) {
                console.log(data);
                if (data.type == "error") {

                } else if (data.type == "success") {
                    console.log(data);
                }
            },
            error: function() {
                alert("FAIL!")
            }
        });
		self.children().fadeOut(300,function(){ $(this).remove() })
		$('<p class="login__title">sign in <br><span class="login-edition">welcome to A.Movie</span></p><p class="success">You have successfully<br> signed in!</p>').appendTo(self)
		.hide().delay(300).fadeIn();
		*/
        // var formInput = self.serialize();
        // $.post(self.attr('action'),formInput, function(data){}); // end post
    }); // end submit

    $('#register-form').submit(function(e) {
        e.preventDefault();
        var error = 0;
        var self = $(this);
        self.find('[type=submit]').attr('disabled', 'disabled');
        var $email = self.find('[type=email]');
        var $pass = self.find('[name=password]');
        var $pass2 = self.find('[name=password2]');
        var emailRegex = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/;
        if (!emailRegex.test($email.val())) {
            //createErrTult("Error! Wrong email!", $email)
            //error++;
        }
        if ($pass.val().length > 1 && $pass.val() != $pass.attr('placeholder')) {
            //$pass.removeClass('invalid_field');
        } else {
            //createErrTult('Error! Wrong password!', $pass)
            //error++;
        }
        var url = self.attr('action');
        var registerfield = self.serialize();
        $.ajax({
            type: "POST",
            url: url,
            data: registerfield,
            success: function(data) {
                self.find('[type=submit]').removeAttr('disabled');
                if (data.type == "error") {
                    for (var i = 0; i < data.errors.length; i++) {
                        self.find('input').each(function(index) {
                            if ($(this).attr('name') == data.errors[i].field) {
                                createErrTult(data.errors[i].message, $(this));
                            }
                        });
                    }
                } else if (data.type == "success") {
                    self.children().fadeOut(300, function() {
                        $("#normal-reg").hide();
                    })
                    $("#success-reg").delay(300).fadeIn();
                }
            },
            error: function() {
                alert_fail();
            }
        });

        /*
		if (error!=0)return;
		self.find('[type=submit]').attr('disabled', 'disabled');
        var url=self.attr('action');
        var registerfield=self.serialize();
        $.ajax({
            type: "POST",
            url: url,
            data: registerfield,
            success: function(data) {
                console.log(data);
                if (data.type == "error") {

                } else if (data.type == "success") {
                    console.log(data);
                }
            },
            error: function() {
                alert("FAIL!")
            }
        });
		self.children().fadeOut(300,function(){ $(this).remove() })
		$('<p class="login__title">Register <br><span class="login-edition">welcome to A.Movie</span></p><p class="success">You have successfully<br> signed in!</p>').appendTo(self)
		.hide().delay(300).fadeIn();
		*/


        // var formInput = self.serialize();
        // $.post(self.attr('action'),formInput, function(data){}); // end post
    }); // end submit

    $('#signupo-form').submit(function(e){
        e.preventDefault();
        $("#signupo-submit").text("...");
        var error = 0;
        var self = $(this);
        var url = self.attr('action');
        var registerfield = self.serialize();
        $.ajax({
            type: "POST",
            url: url,
            data: registerfield,
            success: function(data) {
                if (data.type == "error") {

                } else if (data.type == "success") {
                    $("#signupo-submit").hide();
                    $("#signupo-messege").text("Please, check your email.");
                }
            },
            error: function() {
                alert_fail();
            }
        });
    });

    $('#registration-form').submit(function(e){
        e.preventDefault();
        var error = 0;
        var self = $(this);
        self.find('[type=submit]').attr('disabled', 'disabled');
        var $email = self.find('[type=email]');
        var emailRegex = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/;
        if (!emailRegex.test($email.val())) {
            //createErrTult("Error! Wrong email!", $email)
            //error++;
        }
         else {
            //createErrTult('Error! Wrong password!', $pass)
            //error++;
        }
        var url = self.attr('action');
        var registerfield = self.serialize();
        $.ajax({
            type: "POST",
            url: url,
            data: registerfield,
            success: function(data) {
                self.find('[type=submit]').removeAttr('disabled');
                self.find('input').each(function(index) {
                    $(this).removeClass('invalid_field');
                    $(this).next('.inv-em.alert.alert-danger').remove();
                });
                if (data.type == "error") {
                    for (var i = 0; i < data.errors.length; i++) {
                        self.find('input').each(function(index) {
                            if ($(this).attr('name') == data.errors[i].field) {
                                createErrTult(data.errors[i].message, $(this));
                            }
                        });
                    }
                } else if (data.type == "success") {
                    self.fadeOut(300);
                    $("#success-reg").delay(300).fadeIn();
                } else if (data.type == "info") {
                    var mail = data.data.send_email_again;
                    if (mail) {
                        $("#emailSignupo").val(mail);
                        changeWindow('signupo');
                    }
                }
            },
            error: function() {
                alert_fail();
            }
        });
    });

    $('#edit-registration-form').submit(function(e){
        e.preventDefault();
        var error = 0;
        var self = $(this);
        self.find('[type=submit]').attr('disabled', 'disabled');
        var $email = self.find('[type=email]');
        var emailRegex = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/;
        if (!emailRegex.test($email.val())) {
            //createErrTult("Error! Wrong email!", $email)
            //error++;
        }
         else {
            //createErrTult('Error! Wrong password!', $pass)
            //error++;
        }
        var url = self.attr('action');
        var registerfield = self.serialize();
        $.ajax({
            type: "POST",
            url: url,
            data: registerfield,
            success: function(data) {
                self.find('[type=submit]').removeAttr('disabled');
                self.find('input').each(function(index) {
                    $(this).removeClass('invalid_field');
                    $(this).next('.inv-em.alert.alert-danger').remove();
                });
                if (data.type == "error") {
                    for (var i = 0; i < data.errors.length; i++) {
                        self.find('input').each(function(index) {
                            if ($(this).attr('name') == data.errors[i].field) {
                                createErrTult(data.errors[i].message, $(this));
                            }
                        });
                    }
                } else if (data.type == "success") {
                   $("#success-edit-reg").fadeIn();
                   $("#success-edit-reg").delay(4000).fadeOut();
                }
            },
            error: function() {
                alert_fail();
            }
        });

    });

    $('#edit-password-form').submit(function(e){
        e.preventDefault();
        var error = 0;
        var self = $(this);
        self.find('[type=submit]').attr('disabled', 'disabled');
        var $email = self.find('[type=email]');
        var emailRegex = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/;
        if (!emailRegex.test($email.val())) {
            //createErrTult("Error! Wrong email!", $email)
            //error++;
        }
         else {
            //createErrTult('Error! Wrong password!', $pass)
            //error++;
        }
        var url = self.attr('action');
        var registerfield = self.serialize();
        $.ajax({
            type: "POST",
            url: url,
            data: registerfield,
            success: function(data) {
                self.find('[type=submit]').removeAttr('disabled');
                self.find('input').each(function(index) {
                    $(this).removeClass('invalid_field');
                    $(this).next('.inv-em.alert.alert-danger').remove();
                });
                if (data.type == "error") {
                    for (var i = 0; i < data.errors.length; i++) {
                        self.find('input').each(function(index) {
                            if ($(this).attr('name') == data.errors[i].field) {
                                createErrTult(data.errors[i].message, $(this));
                            }
                        });
                    }
                } else if (data.type == "success") {
                   $("#success-edit-password").fadeIn();
                   $("#success-edit-password").delay(4000).fadeOut();
                }
            },
            error: function() {
                alert_fail();
            }
        });

    });

    $('#forgot-form').submit(function(e) {
        e.preventDefault();
        var error = 0;
        var self = $(this);
        self.find('[type=submit]').attr('disabled', 'disabled');
        var $email = self.find('[type=email]');
        var emailRegex = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/;
        if (!emailRegex.test($email.val())) {
            //createErrTult("Error! Wrong email!", $email)
            //error++;
        } else {
            //createErrTult('Error! Wrong password!', $pass)
            //error++;
        }
        var url = self.attr('action');
        var forgotfield = self.serialize();
        $.ajax({
            type: "POST",
            url: url,
            data: forgotfield,
            success: function(data) {
                self.find('[type=submit]').removeAttr('disabled');
                if (data.type == "error") {
                    for (var i = 0; i < data.errors.length; i++) {
                        self.find('input').each(function(index) {
                            if ($(this).attr('name') == data.errors[i].field) {
                                createErrTult(data.errors[i].message, $(this));
                            }
                        });
                    }
                } else if (data.type == "success") {
                    self.children().fadeOut(300, function() {
                        $("#normal-forgot").hide();
                    })
                    $("#success-forgot").delay(300).fadeIn();
                }
            },
            error: function() {
                alert_fail();
            }
        });
        /*
		if (error!=0)return;
		self.find('[type=submit]').attr('disabled', 'disabled');
        var url=self.attr('action');
        var registerfield=self.serialize();
        $.ajax({
            type: "POST",
            url: url,
            data: registerfield,
            success: function(data) {
                console.log(data);
                if (data.type == "error") {

                } else if (data.type == "success") {
                    console.log(data);
                }
            },
            error: function() {
                alert("FAIL!")
            }
        });
		self.children().fadeOut(300,function(){ $(this).remove() })
		$('<p class="login__title">Register <br><span class="login-edition">welcome to A.Movie</span></p><p class="success">You have successfully<br> signed in!</p>').appendTo(self)
		.hide().delay(300).fadeIn();
		*/


        // var formInput = self.serialize();
        // $.post(self.attr('action'),formInput, function(data){}); // end post
    }); // end submit

    $('.log-out').click(function(e) {
        e.preventDefault();
        var self = $(this);
        var input = self.next('[name=csrfmiddlewaretoken]');
        var url = self.attr('href');
        $.ajax({
            type: "POST",
            url: url,
            data: input,
            success: function(data) {
                if (data.type == "error") {
                    for (var i = 0; i < data.errors.length; i++) {
                        self.find('input').each(function(index) {
                            if ($(this).attr('name') == data.errors[i].field) {
                                createErrTult(data.errors[i].message, $(this));
                            }
                        });
                    }
                } else if (data.type == "success") {
                    window.location = "/";
                }
            },
            error: function() {
                alert_fail();
            }
        });
    });
    $('#signup-confirm-form').submit(function(e) {
        e.preventDefault();
        var self = $(this);
        var code = self.find('[name=code]').val();
        var url = self.attr('action');
        var newurl = url.replace(0, code);
        var codefield = self.serialize();
        self.find('[type=submit]').attr('disabled', 'disabled');
        $.ajax({
            type: "POST",
            url: newurl,
            data: codefield,
            success: function(data) {
                self.find('[type=submit]').removeAttr('disabled');
                if (data.type == "error") {
                    for (var i = 0; i < data.errors.length; i++) {
                        self.find('input').each(function(index) {
                            if ($(this).attr('name') == data.errors[i].field) {
                                createErrTult(data.errors[i].message, $(this));
                            }
                        });
                    }
                    if (data.errors.length == 0) {
                        createErrTult(data.message, $('input[name=code]'));
                    }
                } else if (data.type == "success") {
                    window.location = data.redirect_url;
                }
            },
            error: function() {
                alert_fail();
            }
        });
    });
    $('#forgot-code-form').submit(function(e) {
        e.preventDefault();
        var self = $(this);
        var code = self.find('[name=code]').val();
        var url = self.attr('action');
        var newurl = url.replace(0, code)
        var codefield = self.serialize();
        self.find('[type=submit]').attr('disabled', 'disabled');
        $.ajax({
            type: "POST",
            url: newurl,
            data: codefield,
            success: function(data) {
                self.find('[type=submit]').removeAttr('disabled');
                if (data.type == "error") {
                    for (var i = 0; i < data.errors.length; i++) {
                        self.find('input').each(function(index) {
                            if ($(this).attr('name') == data.errors[i].field) {
                                createErrTult(data.errors[i].message, $(this));
                            }
                        });
                    }
                    if (data.errors.length == 0) {
                        createErrTult(data.message, $('input[name=code]'));
                    }
                } else if (data.type == "success") {
                    createSucTult(data.message, $('input[name=repeat_new_password]'));
                }
            },
            error: function() {
                alert_fail();
            }
        });
    });
    $('#new-pass-form').submit(function(e) {
        e.preventDefault();
        var self = $(this);
        var url = window.location;
        var passfield = self.serialize();
        self.find('[type=submit]').attr('disabled', 'disabled');
        $.ajax({
            type: "POST",
            url: url,
            data: passfield,
            success: function(data) {
                self.find('[type=submit]').removeAttr('disabled');
                if (data.type == "error") {
                    for (var i = 0; i < data.errors.length; i++) {
                        self.find('input').each(function(index) {
                            if ($(this).attr('name') == data.errors[i].field) {
                                createErrTult(data.errors[i].message, $(this));
                            }
                        });
                    }
                    if (data.errors.length == 0) {
                        createErrTult(data.message, $('input[name=repeat_new_password]'));
                    }
                } else if (data.type == "success") {
                    createSucTult(data.message, $('input[name=repeat_new_password]'));
                }
            },
            error: function() {
                alert("FAIL!")
            }
        });
    });

    function createErrTult(text, $elem) {
        $elem.focus();
        $('<p />', {
            'class': 'inv-em alert alert-danger',
            'html': '<span class="icon-warning"></span>' + text + ' <a class="close" data-dismiss="alert" href="#" aria-hidden="true"></a>',
        })
            .appendTo($elem.addClass('invalid_field').parent())
            .insertAfter($elem)
            .delay(4000).animate({
                'opacity': 0
            }, 300, function() {
                $(this).slideUp(400, function() {
                    $elem.removeClass('invalid_field')
                    $(this).remove()
                })
            });
    }

    function createSucTult(text, $elem) {
        $elem.focus();
        $('<p />', {
            'class': 'inv-em alert alert-success',
            'html': '<span class="icon-info"></span>' + text + ' <a class="close" data-dismiss="alert" href="#" aria-hidden="true"></a>',
        })
            .appendTo($elem.parent())
            .insertAfter($elem)
            .delay(4000).animate({
                'opacity': 0
            }, 300, function() {
                $(this).slideUp(400, function() {
                    $(this).remove();
                });
            });
    }
    $('.deletecart').live('click', function(e) {
        e.preventDefault();
        var self = $(this);
        var formatId = $(this).attr('data-format');
        var kioskId = $(this).attr('data-kiosk');
        var upc = $(this).attr('data-upc');
        var href = $(this).attr('data-href');
        var colCart = $('.col-cart').text();
        var csrfmiddlewaretoken = $('input[name=csrfmiddlewaretoken]').val();
        $.ajax({
            type: "POST",
            url: href,
            data: {
                'formatId': formatId,
                'kioskId': kioskId,
                'upc': upc,
                'csrfmiddlewaretoken': csrfmiddlewaretoken
            },
            success: function(data) {
                if (data.type == "error") {} else if (data.type == "success") {
                    $('#cartrefresh').html(data.data.cartTemplate);
                    $('.col-cart').text(data.data.disks_amount);
                }
            },
            error: function() {
                alert_fail();
            }
        });
    });
    $('#purchase').live('click', function(e) {
        e.preventDefault();
        var self = $(this);
        var href = self.attr('data-purchase-url');
        self.attr('disabled', 'disabled');
        // $('.card').removeClass('close').addClass('open');
        var csrfmiddlewaretoken = $('input[name=csrfmiddlewaretoken]').val();
        $.ajax({
            type: "POST",
            url: href,
            data: {
                'csrfmiddlewaretoken': csrfmiddlewaretoken
            },
            success: function(data) {
                if (data.type == "error") {
                    self.removeAttr('disabled');
                    $('.purchasel').hide();
                    $('.alertmodal').addClass('open');
                    $('.alertmodal .login-edition').text(data.message);
                }
                if (data.type == "success") {
                    self.removeAttr('disabled');
                    $('.card').removeClass('close').addClass('open');
                }
                if (data.type == "warning") {
                    self.removeAttr('disabled');
                    $('.purchasel').show();
                    $('.purchasel .alert-warning .wtext').text('');
                    $('.purchasel .alert-warning .wtext').text(data.message);
                    $('.signo').removeClass('close').addClass('open');

                }
            },
            error: function() {
                self.removeAttr('disabled');
                alert_fail();
            }
        });
    });

    $('#card-form').submit(function(e) {
        e.preventDefault();
        var self = $(this);
        var href = self.attr('action');
        $('#pay').attr('disabled', 'disabled');
        var data = self.serialize();
        $.ajax({
            type: "POST",
            url: href,
            data: data,
            success: function(data) {
                $('#pay').removeAttr('disabled');
                if (data.type == "error") {
                    for (var i = 0; i < data.errors.length; i++) {
                        self.find('input').each(function(index) {
                            if ($(this).attr('name') == data.errors[i].field) {
                                createErrTult(data.errors[i].message, $(this));
                            }
                        });
                    }
                } else if (data.type == 'info') {
                    $('.card').removeClass('open')
                    $('#cartrefresh').html(data.data.cartTemplate);
                    $('.col-cart').text(data.data.disks_amount);
                } else if (data.type == "success") {
                    $('.card').removeClass('open')
                    $('#cartrefresh').html(data.data.cartTemplate);
                    $('.col-cart').text(data.data.disks_amount);
                    $('#reservationSuccessOverlay').addClass('open');
                    $('#reservationSuccess').show();
                    $('#secretResCode').text(data.data.secret_code)
                } else if (data.type == "warning") {
                    $('.purchasel .alert-warning .wtext').text('');
                    $('.purchasel .alert-warning .wtext').text(data.message);
                    $('.signo').removeClass('close').addClass('open');
                }
            },
            error: function() {
                self.removeAttr('disabled');
                alert_fail();
            }
        });
    });

    $('#couponForm').submit(function(e) {
        e.preventDefault();
        var jqTarget = $(this),
            data = jqTarget.serialize();
        $.ajax({
            type: "POST",
            url: jqTarget.attr('action'),
            data: data,
            success: function(data) {
                if (data.type == 'success') {
                    $('#cartrefresh').html(data.data.cartTemplate);
                    $('#couponCodeModal').removeClass('open').addClass('close');
                } else if (data.type == 'error') {
                    for (var i = 0; i < data.errors.length; i++) {
                        jqTarget.find('input').each(function(index) {
                            if ($(this).attr('name') == data.errors[i].field) {
                                createErrTult(data.errors[i].message, $(this));
                            }
                        });
                    }
                }
            },
            error: function() {

            }
        })
    })

    function alert_fail() {
        var msg = $('.alert-in-corner');
        msg.fadeIn();
        setTimeout(function(){msg.fadeOut()},3000);
    }

    $(window).scroll(function() {
        if ($('[data-page]') && ($(window).scrollTop() == $(document).height() - $(window).height())) {
            var jqTarget = $('#movies'),
                currentPage = parseInt(jqTarget.attr('data-page'));
            $.ajax({
                type: "GET",
                data: {
                    'page': currentPage + 1,
                    'inf': true
                },
                success: function(data) {
                    if (data.trim()) {
                        $(data).appendTo(jqTarget)
                        jqTarget.attr('data-page', currentPage + 1)
                    }
                }
            })
        }
    });

    $('#addCoupon').live('click', function(e) {
        e.preventDefault();
        $('#couponCodeModal').addClass('open');

    });

    $('.removeCreditCard').live('click', function(e) {
        e.preventDefault();
        var self = $(this);
        var href = self.attr('href');
        $.ajax({
            type: "GET",
            url: href,
            data: {},
            success: function(data) {
                if (data.type == "error") {
                    alert(data.errors);
                } else if (data.type == "success") {
                    $('.alertmodal').addClass('open');
                    $('.alertmodal .login-edition').text(data.message);
                    self.parent().parent().remove();
                }
            },
            error: function() {
                alert_fail();
            }
        });
    });

    $('#addCreditCardForm').submit(function(e){
        e.preventDefault();
        var error = 0;
        var self = $(this);
        var form = $('#addCreditCardForm');
        var $cardNumber = self.find('[name=cardNumber]');
        var $cardHolder = self.find('[name=cardHolder]');
        var $cardExpiryMonth = self.find('[name=cardExpiryMonth]');
        var $cardExpiryYear = self.find('[name=cardExpiryYear]');
        if ($cardNumber.val() == '') {
            createErrTult("Empty field", $cardNumber);error++;
        } else if (!/^\d+$/.test($cardNumber.val())) {
            createErrTult("Need only digits", $cardNumber);error++;
        } else if ($cardNumber.val().length != 16) {
            createErrTult("Need 16 numbers long", $cardNumber);error++;
        }
        if ($cardHolder.val() == '') {
            createErrTult("Empty field", $cardHolder);error++;
        } else if (!/^[A-Za-z0-9_-]*$/.test($cardHolder.val())) {
            createErrTult("Need only latin symbols", $cardHolder);error++;
        } else if ($cardHolder.val().length >= 40) {
            createErrTult("Need less 40 symbols long", $cardHolder);error++;
        }
        if ($cardExpiryMonth.val() == '') {
            createErrTult("Empty field", $cardExpiryMonth);error++;
        } else if (!/^[0-9]*$/.test($cardExpiryMonth.val())) {
            createErrTult("Need only digits", $cardExpiryMonth);error++;
        } else if ((12 < parseInt($cardExpiryMonth.val(), 10)) || (parseInt($cardExpiryMonth.val(), 10) < 1)) {
            createErrTult("In the interval from 1 to 12", $cardExpiryMonth);error++;
        }
        if ($cardExpiryYear.val() == '') {
            createErrTult("Empty field", $cardExpiryYear);error++;
        } else if (!/^[0-9]*$/.test($cardExpiryYear.val())) {
            createErrTult("Need only digits", $cardExpiryYear);error++;
        } else if (!($cardExpiryYear.val().length <= 2)) {
            createErrTult("Need only 2 digits", $cardExpiryYear);error++;
        }
        if (error!=0)return;
        $.ajax({
            type: "POST",
            url: form.attr('action'),
            data: form.serialize(),
            success: function(data) {
                if (data.type == "error") {
                    for (var i = 0; i < data.errors.length; i++) {
                        self.find('input').each(function(index) {
                            if ($(this).attr('name') == data.errors[i].field) {
                                createErrTult(data.errors[i].message, $(this));
                            }
                        });
                    }
                } else if (data.type == "success") {
                    $('.alertmodal').addClass('open');
                    $('.alertmodal .login-edition').text(data.message);
                    $('<tr class="rates rates--top"><td class="rates__obj" name="card_name"><span class="rates__obj-name">'
                        + data.data.card_name
                        +'</span></td><td class="rates__vote" name="card_dt_add">'
                        + data.data.card_dt_add
                        +'</td><td class="rates__result" name="card_remove"><a id="" href="'
                        + data.data.url
                        +'" class="removeCreditCard rates__obj-name">Remove</a></td></tr>').insertBefore($("#tableCreditCardList tr:first"));
                }
            },
            error: function() {
                alert("FAIL");
            }
        })
    });
});