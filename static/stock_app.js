window.addEventListener('load', initialize);

function getColumnIndex(table, headerName) {
    let headers = table.querySelectorAll('th');
    return Array.from(headers).findIndex(header => header.textContent.trim() === headerName);
}

document.addEventListener("DOMContentLoaded", function() {
    if (sessionStorage.getItem("toggled") === null) {
        sessionStorage.setItem("toggled", "false");
    }
    // Initially check and toggle rows if needed
    if (document.title.includes("Grow Kit") && sessionStorage.getItem("toggled") === "true") {
        toggleEmptyRows(true);
    }

    const theme = sessionStorage.getItem('theme');
    document.body.classList.toggle('light-mode', theme === 'light');

    document.getElementById('toggle-theme').addEventListener('click', function () {
        const isLightMode = document.body.classList.toggle('light-mode');
        sessionStorage.setItem('theme', isLightMode ? 'light' : 'dark');
    });

    document.querySelectorAll('input[type="number"], input[type="text"]').forEach(input => {
        input.addEventListener('focus', (event) => {
            event.target.select();
        });
    });

    // Add event listener for the toggle button if applicable
    const toggleButton = document.getElementById('toggle-button');
    if (toggleButton) {
        toggleButton.addEventListener('click', handleToggleClick);
    }
});

function handleToggleClick() {
    const toggled = sessionStorage.getItem("toggled") === "true";
    sessionStorage.setItem("toggled", !toggled);
    toggleEmptyRows(!toggled);
}

function initialize() {
    document.querySelectorAll('input[type="number"]').forEach(input => {
        input.classList.toggle('zero-value', input.value === '0');
        input.addEventListener('change', function() {
            this.classList.toggle('zero-value', this.value === '0');
        });
    });

    if (performance.getEntriesByType('navigation')[0]?.type === 'reload') {
        console.log('reload detected');
        document.getElementById('refreshForm')?.submit();
    }

    setupInputTitles();
}

function setupInputTitles() {
    document.querySelectorAll('table').forEach(table => {
        const headers = table.querySelectorAll('th');
        table.querySelectorAll('tr').forEach(row => {
            const cells = row.querySelectorAll('td');
            if (cells.length > 0) {
                const number = cells[0]?.textContent.trim();
                const name = cells[1]?.textContent.trim();
                cells.forEach((cell, index) => {
                    const header = headers[index]?.textContent || '';
                    cell.querySelectorAll('input[type="number"]').forEach(input => {
                        const title = number ? `${number} - ${name} - ${header}` : `${name} - ${header}`;
                        input.title = title;
                        cell.querySelector('input[type="submit"]')?.setAttribute('title', title);
                    });
                });
            }
        });
    });
}

function updateAllStock() {
    const forms = document.querySelectorAll('form.stock_input');
    let pendingRequests = forms.length;

    forms.forEach(form => {
        const lastRefreshStockInput = form.querySelector('[name="last_refresh_stock"]');
        const submittedStockInput = form.querySelector('[name="submitted_stock"]');

        if (lastRefreshStockInput && submittedStockInput) {
            const lastRefreshStock = parseInt(lastRefreshStockInput.value);
            const submittedStock = parseInt(submittedStockInput.value);

            if (lastRefreshStock !== submittedStock) {
                const formData = new FormData(form);
                fetch(form.action, {
                    method: 'POST',
                    body: formData,
                }).then(response => {
                    if (response.ok) {
                        console.log('Stock updated successfully!');
                        lastRefreshStockInput.value = submittedStock;
                    } else {
                        console.error('Error updating stock');
                    }
                }).catch(error => {
                    console.error('Error updating stock:', error);
                }).finally(() => {
                    pendingRequests--;
                    if (pendingRequests === 0) {
                        location.reload();
                    }
                });
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
    });
}

function toggleEmptyRows(shouldHide) {
    document.querySelectorAll('table').forEach(table => {
        Array.from(table.rows).slice(1).forEach(row => {
            const allEmpty = Array.from(row.querySelectorAll('input[type="number"]')).every(input => parseInt(input.value) === 0);
            row.style.display = shouldHide && allEmpty ? 'none' : '';
        });
    });
}

function toggleEmptyColumns() {
    document.querySelectorAll('table').forEach(table => {
        const headers = table.querySelectorAll('th');
        headers.forEach((_, i) => {
            if (i > 1) { // Skip the first two columns
                const allEmpty = Array.from(table.querySelectorAll(`td:nth-child(${i + 1}) input[type="number"]`)).every(input => parseInt(input.value) === 0);
                const display = allEmpty ? 'none' : '';
                table.querySelectorAll(`td:nth-child(${i + 1})`).forEach(cell => {
                    cell.style.display = display;
                });
            }
        });
    });
}

function getNameColumnIndex(table) {
    return Array.from(table.querySelectorAll('th')).findIndex(header => header.textContent.trim() === "Name");
}

function searchTable() {
    const filter = document.getElementById("searchInput").value.toUpperCase();
    document.querySelectorAll("table").forEach(table => {
        let hasVisibleRow = false;
        Array.from(table.rows).slice(1).forEach(row => { // Skip the header row
            const rowHasMatch = Array.from(row.cells).some(cell => cell.textContent.toUpperCase().includes(filter));
            row.style.display = rowHasMatch ? "" : "none";
            if (rowHasMatch) hasVisibleRow = true;
        });
        table.style.display = hasVisibleRow ? "" : "none";
    });
}

function clearSearch() {
    document.getElementById('searchInput').value = '';
    searchTable();
}

function replaceButtons() {
    document.querySelectorAll('form[action*="update_stock"]').forEach(form => {
        const editButton = document.createElement('button');
        editButton.type = 'button';
        editButton.innerText = 'Edit';
        editButton.onclick = function() {
            const parts = form.action.split('/');
            const id = parts[parts.length - 1];
            const table = parts[parts.length - 2];
            window.location.href = `/edit_product/${table}/${id}`;
        };
        form.parentNode.replaceChild(editButton, form);
    });
}