document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('search');
    const resultsDiv = document.getElementById('results');
    const reserveBtn = document.getElementById('reserve-btn');
    const reserveForm = document.getElementById('reserve-form');
    const formReserve = document.getElementById('form-reserve');
    let selectedBooks = new Set();
    let dataTable = null;

    // Agrega un div para mostrar mensajes
    let messageDiv = document.createElement('div');
    messageDiv.id = 'message';
    messageDiv.style.display = 'none';
    messageDiv.style.margin = '20px 0';
    messageDiv.style.padding = '10px';
    messageDiv.style.backgroundColor = '#dff0d8';
    messageDiv.style.color = '#3c763d';
    messageDiv.style.borderRadius = '5px';
    document.body.insertBefore(messageDiv, document.body.firstChild);

    function renderResults(books) {
        resultsDiv.innerHTML = `
            <div class="table-responsive">
                <table id="books-table" class="table table-striped table-bordered display" style="width:100%">
                    <thead>
                        <tr>
                            <th></th>
                            <th>Estado</th>
                            <th>Título</th>
                            <th>Autor(es)</th>
                            <th>ISBN</th>
                            <th>Editorial</th>
                            <th>Biblioteca</th>
                            <th>País</th>
                            <th>Dirección</th>
                            
                        </tr>
                    </thead>
                    <tbody>
                    </tbody>
                </table>
            </div>
        `;
        const tbody = resultsDiv.querySelector('tbody');
        books.forEach(book => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>
                    <input type="checkbox" class="book-check" data-code="${book.code}" ${book.is_available ? '' : 'disabled'}>
                </td>
                <td>${book.status}</td>
                <td>${book.title}</td>
                <td>${book.authors}</td>
                <td>${book.isbn}</td>
                <td>${book.publisher}</td>
                <td>${book.library}</td>
                <td>${book.country}</td>
                <td>${book.address}</td>
               
            `;
            tbody.appendChild(row);
        });

        // Inicializa DataTables
        if (dataTable) {
            dataTable.destroy();
        }
        dataTable = $('#books-table').DataTable({
            responsive: true,
            ordering: true,
            language: {
                url: "//cdn.datatables.net/plug-ins/1.13.8/i18n/es-ES.json"
            }
        });

        document.querySelectorAll('.book-check').forEach(cb => {
            cb.addEventListener('change', function() {
                if (this.checked) {
                    selectedBooks.add(this.dataset.code);
                } else {
                    selectedBooks.delete(this.dataset.code);
                }
                reserveBtn.style.display = selectedBooks.size > 0 ? 'block' : 'none';
            });
        });
    }

    searchInput.addEventListener('input', function() {
        const query = searchInput.value;
        fetch(`/books/search/?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                renderResults(data.results);
                selectedBooks.clear();
                reserveBtn.style.display = 'none';
                reserveForm.style.display = 'none';
            });
    });

    reserveBtn.addEventListener('click', function() {
        reserveForm.style.display = 'block';
    });

    formReserve.addEventListener('submit', function(e) {
        e.preventDefault();
        const name = document.getElementById('reserver-name').value;
        const email = document.getElementById('reserver-email').value;
        fetch('/books/reserve/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                name: name,
                email: email,
                codes: Array.from(selectedBooks)
            })
        })
        .then(response => response.json())
        .then(data => {
            // Limpiar todo
            reserveForm.style.display = 'none';
            selectedBooks.clear();
            reserveBtn.style.display = 'none';
            searchInput.value = '';
            resultsDiv.innerHTML = '';
            document.getElementById('reserver-name').value = '';
            document.getElementById('reserver-email').value = '';
            // Mostrar mensaje de éxito
            messageDiv.textContent = document.getElementById('msg-success').textContent;
            messageDiv.style.display = 'block';
            setTimeout(() => {
                messageDiv.style.display = 'none';
            }, 4000);
        });
    });

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});