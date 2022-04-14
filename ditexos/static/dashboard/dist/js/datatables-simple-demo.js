window.addEventListener('DOMContentLoaded', event => {
    // Simple-DataTables
    // https://github.com/fiduswriter/Simple-DataTables/wiki

    const datatablesSimple = document.getElementById('datatablesSimple');
    const datatablesSimple2 = document.getElementById('datatablesSimple2');
    const datatables = document.getElementsByClassName('datatable')
    const datatables_scrolling = document.getElementsByClassName('datatable-scrolling')
    const mini_table = document.getElementsByClassName('mini-table')
    const period_table = document.getElementsByClassName('period-table')
    if (datatablesSimple) {
        new simpleDatatables.DataTable(datatablesSimple);
    }
    if (datatablesSimple2) {
        new simpleDatatables.DataTable(datatablesSimple2);
    }
    if (datatables.length > 0) {
        for (i = 0; i < datatables.length; i++) {
            s = new simpleDatatables.DataTable(datatables[i], {
            });
        }
    }
    if (datatables_scrolling.length > 0) {
        for (i = 0; i < datatables_scrolling.length; i++) {
            s = new simpleDatatables.DataTable(datatables_scrolling[i], {
                "scrollY": "500px",
                "scrollCollapse": true,
                "paging": false,
            });
        }
    }
    if (mini_table.length > 0) {
        for (i = 0; i < mini_table.length; i++) {
            new simpleDatatables.DataTable(mini_table[i], {
                searchable: false,
                paging: false,
                info: false
            });
        }
    }
    if (period_table.length > 0) {
        for (i = 0; i < period_table.length; i++) {
            new simpleDatatables.DataTable(period_table[i], {
                searchable: false
            });
        }
    }

});
