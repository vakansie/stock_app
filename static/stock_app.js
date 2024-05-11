window.addEventListener('load', initialize);
function getColumnIndex(table, headerName) {
    let headers = table.querySelectorAll('th');
    return Array.from(headers).findIndex(header => header.textContent.trim() === headerName);
}
document.addEventListener("DOMContentLoaded", function() {
    // Initialize 'toggled' to 'false' if it hasn't been set
    if (sessionStorage.getItem("toggled") === null) {
        sessionStorage.setItem("toggled", "false");
    }
    // Check if a specific string is in the document's title and if the toggle has not been manually triggered
    if (document.title.includes("Grow Kit") && sessionStorage.getItem("toggled") === "false") {
        toggleEmptyRows();
    }
});

function handleToggleClick() {
    // Set a flag to indicate the rows were toggled manually
sessionStorage.setItem("toggled", sessionStorage.getItem("toggled") === "true" ? "false" : "true");
    toggleEmptyRows();
}
function initialize() {
    document.querySelectorAll('input[type="number"]').forEach(input => {
        if (input.value === '0') {
            input.classList.add('zero-value');
        }
        input.addEventListener('change', function() {
            this.value === '0' ? this.classList.add('zero-value') : this.classList.remove('zero-value');
        });
    });
    setupInputTitles();
}
function setupInputTitles() {
    document.querySelectorAll('table').forEach(table => {
        table.querySelectorAll('tr').forEach(row => {
            const cells = row.querySelectorAll('td');
            if (cells.length > 0) {
                // Assuming 'Number' is always the first column and 'Name' is the second
                const number = cells[0].textContent.trim();
                const name = cells[1].textContent.trim();
                
                cells.forEach((cell, index) => {
                    const headers = table.querySelectorAll('th');
                    let header = headers[index] ? headers[index].textContent : '';

                    let inputs = cell.querySelectorAll('input[type="number"]');
                    inputs.forEach(input => {
                        // Set title for the input
                        input.title = number ? `${number} - ${name} - ${header}` : `${name} - ${header}`;

                        // Set the same title for the button to the right of the input, if it exists
                        let button = cell.querySelector('input[type="submit"]');
                        if (button) {
                            button.title = input.title;
                        }
                    });
                });
            }
        });
    });
}
// JavaScript to handle submitting all forms at once
function updateAllStock() {
    document.querySelectorAll('form').forEach(form => {
        const lastRefreshStock = parseInt(form.querySelector('[name="last_refresh_stock"]').value);
        const submittedStock = parseInt(form.querySelector('[name="submitted_stock"]').value);
        if (lastRefreshStock !== submittedStock) {
            const formData = new FormData(form);
            fetch(form.action, {
                method: 'POST',
                body: formData,
            }).then(response => {
                if (response.ok) {
                    console.log('Stock updated successfully!');
                } else {
                    console.error('Error updating stock');
                }
            });
        }
    });
}
function toggleEmptyRows() {
    const tables = document.querySelectorAll('table');
    tables.forEach(table => {
        // Ensure only non-header rows are toggled
        table.querySelectorAll('tr').forEach(row => {
            if (row !== table.rows[0]) { // Skip the header row
                const inputs = row.querySelectorAll('input[type="number"]');
                const allEmpty = Array.from(inputs).every(input => input.value === '0');
                row.style.display = row.style.display === 'none' ? '' : (allEmpty ? 'none' : '');
            }
        });
    });
}
function toggleEmptyColumns() {
    const tables = document.querySelectorAll('table');
    tables.forEach(table => {
        const numCols = table.querySelectorAll('th').length;
        for (let i = 2; i <= numCols; i++) { // Start from 2 to skip the name column
            const inputs = table.querySelectorAll('td:nth-child(' + i + ') input[type="number"]');
            const allEmpty = Array.from(inputs).every(input => input.value === '0');
            const colVisibility = allEmpty ? 'none' : '';
            // Only toggle td elements, keep th always visible
            table.querySelectorAll('td:nth-child(' + i + ')').forEach(cell => {
                cell.style.display = cell.style.display === 'none' ? '' : colVisibility;
            });
        }
    });
}
function getNameColumnIndex(table) {
    // Get the header row (assuming it's the first row in the table)
    let headers = table.querySelectorAll('th');
    // Find the index of the "Name" column
    let nameIndex = Array.from(headers).findIndex(header => header.textContent.trim() === "Name");
    return nameIndex; // Return the index (+1 since nth-child is 1-based)
}
function searchTable() {
    var input, filter, tables, tr, td, i, j;
    input = document.getElementById("searchInput");
    filter = input.value.toUpperCase();
    tables = document.querySelectorAll("table"); // Select all tables

    // Loop through all tables
    tables.forEach(table => {
        tr = table.getElementsByTagName("tr");
        let hasVisibleRow = false; // Track if there's any visible row

        // Loop through all rows in the current table, skipping the header
        for (i = 1; i < tr.length; i++) {
            let rowHasMatch = false; // Track if the current row has a match
            td = tr[i].getElementsByTagName("td");
            for (j = 0; j < td.length; j++) {
                if (td[j].textContent.toUpperCase().indexOf(filter) > -1) {
                    rowHasMatch = true;
                    break; // Stop checking more cells, one match is enough
                }
            }
            tr[i].style.display = rowHasMatch ? "" : "none"; // Show or hide the row based on match
            if (rowHasMatch) hasVisibleRow = true; // Update table visibility flag
        }

        // Hide the table if no rows are visible
        table.style.display = hasVisibleRow ? "" : "none";
    });
}

function replaceButtons() {
    var updateForms = document.querySelectorAll('form[action*="update_stock"]');
    updateForms.forEach(function(form) {
        var editButton = document.createElement('button');
        editButton.type = 'button';
        editButton.innerText = 'Edit';
        editButton.onclick = function() {
            var actionUrl = form.action;
            // Split the URL by '/' and take the last element as the ID
            var parts = actionUrl.split('/');
            var id = parts[parts.length - 1];  // The ID is the last part of the URL
            var table = parts[parts.length - 2];
            console.log('table', table)
            window.location.href = `/edit_product/${table}/${id}`;  // Redirect to the edit page with the ID
        };
        form.parentNode.replaceChild(editButton, form);
    });
}