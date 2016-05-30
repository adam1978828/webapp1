// Douglas Crockford function
String.prototype.supplant = function(o) {
    return this.replace(/{([^{}]*)}/g,
        function(a, b) {
            var r = o[b];
            return typeof r === 'string' || typeof r === 'number' ? r : a;
        }
    );
};

var CouponProcessor = (function(window, undefined) {
    var inline_input = '<input type="text" data-percentage={percents} class="inline-edit" name="params">',
        COUPON_TYPES = [
            "",
            "Don't pay anything for first night rental!",
            "Get discount on the first night for {d}%!".supplant({
                d: inline_input.supplant({
                    //percents: 'false'
                    percents: 'true'
                })
            }),
            // this is not obligatory for now, as this coupon (One Free Rental) is out for now
            // but indexes in db are still the same, so this thing make processor work correctly
            // so, you need either to leave it here or change db indexing and remove it
            // OR eventually to rewrite processor ;)
            "All nights beyond the first night are free!",
            "Rent {d} disks, get {d} free for first night!".supplant({
                d: inline_input.supplant({
                    percents: 'false'
                })
            }),
            "Rent {d1} disks, get {d2}% discount!".supplant({
                d1: inline_input.supplant({
                    percents: 'false'
                }),
                d2: inline_input.supplant({
                    //percents: 'false'
                    percents: 'true'
                })
            }),
            "Get ${d} discount!".supplant({
                d: inline_input.supplant({
                    percents: 'false'
                })
            }),
            "Rent {d1} disks, get {d1} with {d2}% discount on the first night and {d2}% discount on the next nights!".supplant({
                d1: inline_input.supplant({
                    percents: 'false'
                }),
                d2: inline_input.supplant({
                    percents: 'true'
                })
            })
        ];

    function getPatternDescription(id) {
        return COUPON_TYPES[id]
    }

    return {
        describe: getPatternDescription
    };
})(window);

couponTypeId = $('#couponTypeId');
couponTypeId.val('').trigger('chosen:updated');
$('#addCoupon').trigger('reset');
couponTypeId.on('change', function(evt, params) {
    var explanation = $('#params');
    var couponType = $("#couponTypeId option:selected").val();
    var input_elements = $('input.inline-store');
    var params_values = [];

    input_elements.each(function(index, elem) {
        params_values.push(parseFloat($(elem).val()));
    });
    if ((params === undefined) && (couponType === undefined) ) {
        explanation.parents('.row').addClass('hidden')
    } else {
        couponType = params !== undefined ? params.selected : couponType;
        $('input.inline-store').remove();
        explanation.parents('.row').removeClass('hidden');
        explanation.html(CouponProcessor.describe(couponType));
        inlineEdit = $('input.inline-edit');
        inlineEdit.each(function() {
            if (this.value.length != 0) {
                this.style.width = this.value.length * 10 + 'px';
            }
            else
                this.style.width = '56px';
        });

        for (i = 0; i < inlineEdit.length; i++) {
            if (inlineEdit[i].getAttribute('data-percentage') == 'true'){
                inlineEdit[i].value = params_values[i]*100 || ''
            }
            else{
                inlineEdit[i].value = params_values[i] !== 0 ? params_values[i] || '' : 0
                }
        }

        //$$.utils.forms.resize()

    }
});
couponTypeId.trigger('change');

$('#submitCoupon').on('click', function(e) {
    e.preventDefault();
    var form = $('#addCoupon');
    $('#params input').each(function() {
        if (this.getAttribute('data-percentage') == 'true') {
            this.value = parseFloat(this.value) / 100.0;
        }
    });
    $.ajax({
        type: "POST",
        url: form.attr('action'),
        data: form.serializeObject(),
        success: function(data) {
            //if (data.data.reload) {location.reload();}
            if (data.type == "error") {
                $$.showModalMessage(data.type, data.message, null);
                $$.displayServerValidationResults(data)
            } else if (data.type == "success") {
                $$.showModalMessage(data.type, data.message, function(){window.location = data.redirect_url;});

                form.trigger('reset');
                $('#params').parents('.row').removeClass('hidden');
                $('#couponTypeId').val('').trigger('chosen:updated');
            }
        },
        error: function() {
            alert("FAIL");
        }
    })
});

$('#submitCouponEdit').on('click', function(e) {
    e.preventDefault();
    var form = $('#addCoupon');
    $('#params input').each(function() {
        if (this.getAttribute('data-percentage') == 'true') {
            this.value = parseFloat(this.value) / 100.0;
        }
    });
    $.ajax({
        type: "POST",
        url: form.attr('action'),
        data: form.serializeObject(),
        success: function(data) {
            //if (data.data.reload) {location.reload();}
            if (data.type == "error") {
                $$.displayServerValidationResults(data)
            } else if (data.type == "success") {
                if (data.data.focus) {
                   var options = [
                        //data.data.count,
                        data.data.couponId,
                        data.data.type,
                        data.data.code,
                        data.data.formula,
                        data.data.usageAmount,
                        data.data.perCardUsage,
                        data.data.dtStart,
                        data.data.dtEnd,
                        data.data.company,
                        //'<a class="removecoupon" href="' + data.data.url + '"><i class="icon-remove"></i></a></div>'
                    ];
                } else {
                    var options = [
                        //data.data.count,
                        data.data.couponId,
                        data.data.type,
                        data.data.code,
                        data.data.formula,
                        data.data.usageAmount,
                        data.data.perCardUsage,
                        data.data.dtStart,
                        data.data.dtEnd,
                        //'<a class="removecoupon" href="' + data.data.url + '"><i class="icon-remove"></i></a></div>'
                    ];
                }

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
                //form.trigger('reset');
                $('#params').parents('.row').removeClass('hidden');
                //$('#couponTypeId').val('').trigger('chosen:updated');
            }
        },
        error: function() {
            alert("FAIL");
        }
    });
    $('#params input').each(function() {
        if (this.getAttribute('data-percentage') == 'true') {
            this.value = parseFloat(this.value) * 100.0;
        }
    });
});

$('#couponsTable').on('click', '.removecoupon', function(e) {
    e.preventDefault();
    var then = $(this);
    $.ajax({
        type: "POST",
        url: $(this).attr('href'),
        success: function(data) {
            $$.showModalMessage(data.type, data.message, null);
            if (data.type == "success") {
                var tr = then.parent().parent();
                tr.find('span.budge').removeClass('green').addClass('red').html('Yes');
                tr.find('.restorecoupon').removeClass('hidden');
                then.addClass('hidden');

                $('#couponsTable').dataTable().fnDraw()
            }
        },
        error: function() {
            alert("FAIL")
        }
    })
});

$('#couponsTable').on('click', '.restorecoupon', function(e) {
    e.preventDefault();
    var then = $(this);
    $.ajax({
        type: "POST",
        url: $(this).attr('href'),
        success: function(data) {
            $$.showModalMessage(data.type, data.message, null);
            if (data.type == "success") {
                var tr = then.parent().parent();
                tr.find('span.budge').removeClass('red').addClass('green').html('No');
                tr.find('.removecoupon').removeClass('hidden');
                then.addClass('hidden');

                $('#couponsTable').dataTable().fnDraw()
            }
        },
        error: function() {
            alert("FAIL")
        }
    })
});

$('#genCouponCode').on('click', function(e) {
    e.preventDefault();
    var codeInput = $(e.target).parent().siblings('input'),
        numset = '0123456789',
        charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
        codePattern = 'C{l}{d1}{d2}3{c}',
        randomChar = function() {
            return charset[Math.floor(Math.random() * charset.length)]
        },
        randomDigit = function() {
            return numset[Math.floor(Math.random() * numset.length)]
        },
        rndChar = randomChar(),
        rndDigit1 = randomDigit(),
        rndDigit2 = randomDigit();

    codeInput.val(codePattern.supplant({
        l: rndChar,
        d1: rndDigit1,
        d2: rndDigit2,
        c: (rndChar.charCodeAt(0) + parseInt(rndDigit1) + parseInt(rndDigit2)) % 10
    }))
});