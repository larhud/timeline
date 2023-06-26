(function ($) {
    $(document).ready(function () {
        $('#btn-enviar').click(function (event) {
            event.preventDefault();

            let form = $('#form-contato');
            let formData = new FormData(form[0]);

            $.ajax({
                url: form.attr('action'),
                type: "POST",
                data: formData,
                cache: false,
                processData: false,
                contentType: false,
                success: function (data) {
                    $('.validation').empty();

                    if (data.success) {
                        $('#__all___message').append('<span class="text-success">' + data.success[0] + '</span>');
                        form[0].reset();
                    } else {
                        for (let name in data) {
                            let element = $('#' + name + '_message');
                            data[name].forEach(function (item) {
                                element.append('<small class="text-danger">' + item + '</small>');
                            });
                        }
                    }
                },
                error: function (request, status, error) {
                    console.log(request.responseText);
                }
            });
        })
        ;
    });
})(jQuery);