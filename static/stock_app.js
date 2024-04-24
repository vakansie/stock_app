
        // JavaScript to handle submitting all forms at once and to grey out zero value inputs
        function updateAllStock() {
            document.querySelectorAll('form').forEach(form => {
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
            });
        }

        function initialize() {
            document.querySelectorAll('input[type="number"]').forEach(input => {
                if (input.value === '0') {
                    input.classList.add('zero-value');
                }
                input.addEventListener('change', function() {
                    this.value === '0' ? this.classList.add('zero-value') : this.classList.remove('zero-value');
                });
                let name = input.closest('tr').querySelector('td').textContent;
                let header = input.closest('table').querySelector('th:nth-child(' + (input.closest('td').cellIndex + 1) + ')').textContent;
                input.title = name + ' - ' + header;
            });
        }
            setupInputTitles();
            document.addEventListener("DOMContentLoaded", function() {
                // Check if a specific string is in the document's title
                if (document.title.includes("Grow Kit")) {
                    toggleEmptyRows();
                }
            });       
        window.addEventListener('load', initialize);

        function getColumnIndex(table, headerName) {
            let headers = table.querySelectorAll('th');
            return Array.from(headers).findIndex(header => header.textContent.trim() === headerName);
        }

        function setupInputTitles() {
            document.querySelectorAll('input[type="number"]').forEach(input => {
                if (input.value === '0') {
                    input.classList.add('zero-value');
                }
                input.addEventListener('change', function() {
                    this.value === '0' ? this.classList.add('zero-value') : this.classList.remove('zero-value');
                });
                // Get the parent table of the current input
                let table = input.closest('table');
                let nameColumnIndex = getColumnIndex(table, "Name") + 1; // +1 because nth-child is 1-based
                let numberColumnIndex = getColumnIndex(table, "Number") + 1;
                let nameTd = input.closest('tr').querySelector(`td:nth-child(${nameColumnIndex})`);
                let numberTd = input.closest('tr').querySelector(`td:nth-child(${numberColumnIndex})`);
                let name = nameTd.textContent.trim();
                let number = numberTd ? numberTd.textContent.trim() : null; // Check if Number column exists
                let header = input.closest('table').querySelector('th:nth-child(' + (input.closest('td').cellIndex + 1) + ')').textContent;
        
                // Modify title to include Number if available
                input.title = number ? `${number} - ${name} - ${header}` : `${name} - ${header}`;
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
            var input, filter, table, tr, tdNumber, tdName, i;
            input = document.getElementById("searchInput");
            filter = input.value.toUpperCase();
            table = document.getElementById("Seed Inventory");
            tr = table.getElementsByTagName("tr");
        
            // Loop through all table rows, and hide those who don't match the search query
            for (i = 1; i < tr.length; i++) { // start with 1 to avoid the header
                tdNumber = tr[i].getElementsByTagName("td")[0]; // Number column
                tdName = tr[i].getElementsByTagName("td")[1]; // Name column
                if (tdNumber || tdName) {
                    if (tdNumber.textContent.toUpperCase().indexOf(filter) > -1 || tdName.textContent.toUpperCase().indexOf(filter) > -1) {
                        tr[i].style.display = "";
                    } else {
                        tr[i].style.display = "none";
                    }
                }
            }
        }