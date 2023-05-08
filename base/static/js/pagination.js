/* Depende do plugin pagination.js 2.6.0 (versão mínima) */
function scrollToElement(el) {
    if (window.matchMedia("(max-width: 810px)").matches) {
        jQuery('html').animate({scrollTop: (el.offset().top)}, 500);
    }
}

function initPagination(name, data_url, callback) {
    let container = jQuery("#pagination-" + name);
    let dataContainer = jQuery("#item-container-" + name);

    container.pagination({
        locator: "items",
        pageSize: 10,
        dataSource: data_url,
        totalNumberLocator: function (data) {
            // data = retorno da url indicada em dataSource
            return data.num_pages;
        },
        showPageNumbers: true,
        showPrevious: false,
        showNext: false,
        showFirstOnEllipsisShow: true,
        showLastOnEllipsisShow: true,
        alias: {
            pageNumber: 'page'
        },
        afterPageOnClick: function () {
            scrollToElement(dataContainer);
        },
        ajax: {
            beforeSend: function () {
                container.prev().html("Carregando dados...");
            },
        },
        callback: callback
    });
}

function paginationDataAsTable(data, pagination) {
    let fields = Object.keys(pagination.originalResponse.fields);
    let header = Object.values(pagination.originalResponse.fields);
    let dataHtml = '<table><thead><tr>';

    header.forEach(function (item) {
        dataHtml += `<th>${item}</th>`;
    });

    dataHtml += '</tr></thead><tbody>';

    data.forEach(function (item) {
        let rowHtml = '<tr>';

        fields.forEach(function (field) {
            rowHtml +=
                `<td>${item[field]}</td>`;
        });

        rowHtml += '</tr>';

        dataHtml += rowHtml;
    });

    dataHtml += "</table>";

    pagination.el.parent().prev().html(dataHtml);
}