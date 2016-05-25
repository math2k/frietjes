$(document).ready(function () {
    $('.price-toggle').click(function () {
        if ($(this).hasClass("active")) {
            $('.price').hide();
            $(this).removeClass('active');
        } else {
            $('.price').show();
            $(this).addClass('active');
        }
    });
    $('.add-tooltip').tooltip();

    $('.sidebar').theiaStickySidebar({
        additionalMarginTop: 60
    });

    $('.add-static-tooltip').tooltip({'trigger': 'manual'}).tooltip('show');

    dt = $('.datetimepicker').datetimepicker({
        icons: {
            // inverted, check bootstrap-datetimepicker.min.js:374
            time: 'fa fa-calendar',
            date: 'fa fa-clock-o',
            up: 'fa fa-chevron-up',
            down: 'fa fa-chevron-down',
            previous: 'fa fa-chevron-left',
            next: 'fa fa-chevron-right',
            today: 'fa glyphicon-screenshot',
            clear: 'fa fa-trash',
            close: 'fa fa-remove'
        },
        format: 'D/M/YYYY HH:mm',
        stepping: 5,
        sideBySide: false,
        showClear: true,
        showClose: true,
        useCurrent: false
        //defaultDate: moment.utc().hour(12).minute(00)
    });
});

$(document).on('submit', '.confirm-form', function () {
    return confirm('Are you sure ?');
});

$(document).on('show.bs.modal', '#image-modal', function (event) {
    var button = $(event.relatedTarget);
    var modal = $(this);
    $(this).find('.modal-body').css({
        width: 'auto', //probably not needed
        height: 'auto', //probably not needed
        'max-height': '100%'
    });
    modal.find('.modal-body').html("<img style='width: 100%; height: 100%' src='" + button.data('img') + "' />");

});
$.noty.defaults = $.extend(true, $.noty.defaults, {
    timeout: 5000,
    killer: true,
    layout: 'topCenter',
    theme: 'relax',
    animation: {
        open: 'animated slideInDown', // Animate.css class names
    }
});

