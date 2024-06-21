window.addEventListener('load', initialize);

function getColumnIndex(table, headerName) {
    var headers = table.querySelectorAll('th');
    for (var i = 0; i < headers.length; i++) {
        if (headers[i].textContent.trim() === headerName) {
            return i;
        }
    }
    return -1;
}

document.addEventListener("DOMContentLoaded", function() {
    if (sessionStorage.getItem("toggled") === null) {
        sessionStorage.setItem("toggled", "false");
    }
    if (document.title.indexOf("Grow Kit") !== -1 && sessionStorage.getItem("toggled") === "true") {
        toggleEmptyRows(true);
    }

    var theme = sessionStorage.getItem('theme');
    if (theme === 'light') {
        document.body.classList.add('light-mode');
    } else {
        document.body.classList.remove('light-mode');
    }

    document.getElementById('toggle-theme').addEventListener('click', function () {
        var isLightMode = document.body.classList.contains('light-mode');
        if (isLightMode) {
            document.body.classList.remove('light-mode');
            sessionStorage.setItem('theme', 'dark');
        } else {
            document.body.classList.add('light-mode');
            sessionStorage.setItem('theme', 'light');
        }
    });

    var inputs = document.querySelectorAll('input[type="number"], input[type="text"]');
    for (var i = 0; i < inputs.length; i++) {
        inputs[i].addEventListener('focus', function(event) {
            event.target.select();
        });
    }

    var toggleButton = document.getElementById('toggle-button');
    if (toggleButton) {
        toggleButton.addEventListener('click', handleToggleClick);
    }

    // Initial update for sticky header
    updateTableHeaderTop();

    // Update on window resize
    window.addEventListener('resize', updateTableHeaderTop);
});

function handleToggleClick() {
    var toggled = sessionStorage.getItem("toggled") === "true";
    sessionStorage.setItem("toggled", !toggled);
    toggleEmptyRows(!toggled);
}

function initialize() {
    var inputs = document.querySelectorAll('input[type="number"]');
    for (var i = 0; i < inputs.length; i++) {
        inputs[i].classList.toggle('zero-value', inputs[i].value === '0');
        inputs[i].addEventListener('change', function() {
            this.classList.toggle('zero-value', this.value === '0');
        });
    }

    var navigationEntries = performance.getEntriesByType ? performance.getEntriesByType('navigation') : [];
    if (navigationEntries.length > 0 && navigationEntries[0].type === 'reload') {
        console.log('reload detected');
        var refreshForm = document.getElementById('refreshForm');
        if (refreshForm) {
            refreshForm.submit();
        }
    }

    setupInputTitles();
}

function setupInputTitles() {
    var tables = document.querySelectorAll('table');
    for (var t = 0; t < tables.length; t++) {
        var table = tables[t];
        var headers = table.querySelectorAll('th');
        var rows = table.querySelectorAll('tr');
        for (var r = 0; r < rows.length; r++) {
            var row = rows[r];
            var cells = row.querySelectorAll('td');
            if (cells.length > 0) {
                var number = cells[0].textContent.trim();
                var name = cells[1].textContent.trim();
                for (var c = 0; c < cells.length; c++) {
                    var cell = cells[c];
                    var header = headers[c] ? headers[c].textContent : '';
                    var inputs = cell.querySelectorAll('input[type="number"]');
                    for (var i = 0; i < inputs.length; i++) {
                        var input = inputs[i];
                        var title = number ? (number + " - " + name + " - " + header) : (name + " - " + header);
                        input.title = title;
                        var submitInput = cell.querySelector('input[type="submit"]');
                        if (submitInput) {
                            submitInput.setAttribute('title', title);
                        }
                    }
                }
            }
        }
    }
}

function updateAllStock() {
    var forms = document.querySelectorAll('form.stock_input');
    var pendingRequests = forms.length;

    for (var i = 0; i < forms.length; i++) {
        var form = forms[i];
        var lastRefreshStockInput = form.querySelector('[name="last_refresh_stock"]');
        var submittedStockInput = form.querySelector('[name="submitted_stock"]');

        if (lastRefreshStockInput && submittedStockInput) {
            var lastRefreshStock = parseInt(lastRefreshStockInput.value);
            var submittedStock = parseInt(submittedStockInput.value);

            if (lastRefreshStock !== submittedStock) {
                var formData = new FormData(form);
                var xhr = new XMLHttpRequest();
                xhr.open('POST', form.action, true);
                xhr.onload = function() {
                    if (xhr.status >= 200 && xhr.status < 300) {
                        console.log('Stock updated successfully!');
                        lastRefreshStockInput.value = submittedStock;
                    } else {
                        console.error('Error updating stock');
                    }
                    pendingRequests--;
                    if (pendingRequests === 0) {
                        location.reload();
                    }
                };
                xhr.onerror = function() {
                    console.error('Error updating stock:', xhr.statusText);
                    pendingRequests--;
                    if (pendingRequests === 0) {
                        location.reload();
                    }
                };
                xhr.send(formData);
            } else {
                pendingRequests--;
                if (pendingRequests === 0) {
                    location.reload();
                }
            }
        } else {
            console.error('Missing required input fields in form:', form);
            pendingRequests--;
            if (pendingRequests === 0) {
                location.reload();
            }
        }
    }
}

function toggleEmptyRows(shouldHide) {
    var tables = document.querySelectorAll('table');
    for (var t = 0; t < tables.length; t++) {
        var table = tables[t];
        var rows = table.rows;
        for (var r = 1; r < rows.length; r++) {
            var row = rows[r];
            var allEmpty = true;
            var inputs = row.querySelectorAll('input[type="number"]');
            for (var i = 0; i < inputs.length; i++) {
                if (parseInt(inputs[i].value) !== 0) {
                    allEmpty = false;
                    break;
                }
            }
            row.style.display = shouldHide && allEmpty ? 'none' : '';
        }
    }
}

function toggleEmptyColumns() {
    var tables = document.querySelectorAll('table');
    for (var t = 0; t < tables.length; t++) {
        var table = tables[t];
        var headers = table.querySelectorAll('th');
        for (var i = 2; i < headers.length; i++) {
            var allEmpty = true;
            var cells = table.querySelectorAll('td:nth-child(' + (i + 1) + ') input[type="number"]');
            for (var j = 0; j < cells.length; j++) {
                if (parseInt(cells[j].value) !== 0) {
                    allEmpty = false;
                    break;
                }
            }
            var display = allEmpty ? 'none' : '';
            for (var c = 0; c < cells.length; c++) {
                cells[c].style.display = display;
            }
        }
    }
}

function getNameColumnIndex(table) {
    var headers = table.querySelectorAll('th');
    for (var i = 0; i < headers.length; i++) {
        if (headers[i].textContent.trim() === "Name") {
            return i;
        }
    }
    return -1;
}

function searchTable() {
    var filter = document.getElementById("searchInput").value.toUpperCase();
    var tables = document.querySelectorAll("table");
    for (var t = 0; t < tables.length; t++) {
        var table = tables[t];
        var hasVisibleRow = false;
        var rows = table.rows;
        for (var r = 1; r < rows.length; r++) {
            var row = rows[r];
            var rowHasMatch = false;
            var cells = row.cells;
            for (var c = 0; c < cells.length; c++) {
                if (cells[c].textContent.toUpperCase().indexOf(filter) > -1) {
                    rowHasMatch = true;
                    break;
                }
            }
            row.style.display = rowHasMatch ? "" : "none";
            if (rowHasMatch) hasVisibleRow = true;
        }
        table.style.display = hasVisibleRow ? "" : "none";
    }
}

function clearSearch() {
    document.getElementById('searchInput').value = '';
    searchTable();
}

function replaceButtons() {
    var forms = document.querySelectorAll('form[action*="update_stock"]');
    for (var i = 0; i < forms.length; i++) {
        var form = forms[i];
        var editButton = document.createElement('button');
        editButton.type = 'button';
        editButton.innerText = 'Edit';
        editButton.onclick = (function(f) {
            return function() {
                var parts = f.action.split('/');
                var id = parts[parts.length - 1];
                var table = parts[parts.length - 2];
                window.location.href = '/edit_product/' + table + '/' + id;
            };
        })(form);
        form.parentNode.replaceChild(editButton, form);
    }
}

// Function to update the top value of the sticky table header based on search-container height
function updateTableHeaderTop() {
    var searchContainer = document.getElementById('search-container');
    var tableHeader = document.getElementById('table-header');

    if (searchContainer && tableHeader) {
        var searchContainerHeight = searchContainer.offsetHeight;
        var headerCells = tableHeader.querySelectorAll('th');

        for (var i = 0; i < headerCells.length; i++) {
            headerCells[i].style.top = searchContainerHeight + 'px';
        }
    }
}
