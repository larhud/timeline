(function () {
    $(document).ready(function () {
        function scrollToElement(el) {
            if (window.matchMedia("(max-width: 810px)").matches) {
                $('html').animate({scrollTop: (el.offset().top)}, 500);
            }
        }

        function initPaginator(name, order = 'pk') {
            let container = $("#pagination-" + name);
            let dataContainer = $("#item-container-" + name);

            container.pagination({
                locator: "items",
                pageSize: 4,
                dataSource: window.__lista_de_termos__ + '?order_by=' + order,
                totalNumberLocator: function (data) {
                    // data = retorno da url indicada em dataSource
                    return data.total;
                },
                showPageNumbers: true,
                showPrevious: true,
                showNext: true,
                nextText: 'Próxima <i class="fa-solid fa-arrow-right"></i>',
                prevText: '<i class="fa-solid fa-arrow-left"></i> Anterior',
                showFirstOnEllipsisShow: true,
                showLastOnEllipsisShow: true,
                afterPreviousOnClick: function () {
                    scrollToElement(dataContainer);
                },
                afterNextOnClick: function () {
                    scrollToElement(dataContainer);
                },
                afterPageOnClick: function () {
                    scrollToElement(dataContainer);
                },
                ajax: {
                    beforeSend: function () {
                        container.prev().html("Loading data...");
                    },
                },
                callback: function (response, pagination) {
                    let dataHtml = '<div class="itens">';

                    $.each(response, function (index, item) {
                        dataHtml +=
                            '<div class="item"><img src="' + item.imagem + '" alt="' + item.termo +
                            '"/><div class="conteudo"><h4>' + item.termo + '</h4>';
                        dataHtml += '<p>' + item.texto + '</p>';
                        dataHtml += '<a href="' + item.url + '">Acessar timeline <i class="fa-solid fa-arrow-right"></i></a></div></div>';
                    });

                    dataHtml += "</div>";

                    container.prev().html(dataHtml);
                },
            });
        }

        let selectOrdem = $('#ordem-termos');

        selectOrdem.change(function () {
            initPaginator('termos', $(this).val());
        });

        selectOrdem.trigger('change');
    });
})(jQuery);
