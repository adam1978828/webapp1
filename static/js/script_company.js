$(document).ready(function() {

    $("#dialog").dialog({
        autoOpen: false
    });


    $('#f_create_kiosk').validate({
        submitHandler: function(form) {
            var data = $(form).serializeObject();
            data['geolocation'] = $('#mapCanvas').attr('data-marker');
            $.ajax({
                type: $(form).attr('method'),
                url: $(form).attr('action'),
                data: data,
                dataType: 'json',
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
                        //window.location = url;
                    }
                    $$.showModalMessage(data.type, data.message, null);
                },
                error: function() {
                    alert("FAIL!");
                }
            });
        }
    });

    // this must be in js file with helpers
    var rand_pass = function(length) {
        var s = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
        var pass = '';
        for (i = 0; i < length; i++) {
            pass += s[Math.floor((Math.random() * s.length))];
        }
        return pass
    };

    $('#bt_generate_pass').click(function() {
        $("#f_admin_pass").val(rand_pass(8))
    });

    /*$("#btn_upload_logo").on('click', (function(e){
        e.preventDefault();
        $('#upload_logo').trigger( "click" );
    }));
    $("#upload_logo").change(function(){
        $("#upload_logo_form").trigger('submit');
    });
    $("#upload_logo_form").on('submit',(function(e) {
        e.preventDefault();
        var formData = new FormData(this);

        $.ajax({
            type:'POST',
            url: $(this).attr('action'),
            data:formData,
            cache:false,
            contentType: false,
            processData: false,
            success:function(data){
                $("img#img_logo").attr('src', '/media/'+data.src);
            },
            error: function(data){
                console.log("error");
                console.log(data);
            }
        });
    }));*/

    $("#f_company_logo").change(function() {
        var $img = $('#f_img_logo');
        if (this.files && this.files[0]) {
            var reader = new FileReader();

            reader.onload = function(e) {
                $img.attr('src', e.target.result);
            };

            reader.readAsDataURL(this.files[0]);
        }
    });


});