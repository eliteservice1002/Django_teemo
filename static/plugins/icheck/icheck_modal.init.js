$('.check_modal').each(function() {
    var ck = $(this).attr('data-checkbox') ? $(this).attr('data-checkbox') : 'icheckbox_minimal-red';
    var rd = $(this).attr('data-radio') ? $(this).attr('data-radio') : 'iradio_minimal-red';

    if (ck.indexOf('_line') > -1 || rd.indexOf('_line') > -1) {
        $(this).iCheck({
            checkboxClass: ck,
            radioClass: rd,
            insert: '<div class="icheck_line-icon"></div>' + $(this).attr("data-label")
        });
    } else {
        $(this).iCheck({
            checkboxClass: ck,
            radioClass: rd
        });
    }
});