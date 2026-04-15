document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('search');
    const resultsDiv = document.getElementById('results');
    const reserveBtn = document.getElementById('reserve-btn');
    const reserveForm = document.getElementById('reserve-form');
    const formReserve = document.getElementById('form-reserve');
    let selectedBooks = new Set();
    let dataTable = null;    let altchaSolutionValue = null; // Almacenar la solución cuando se verifique
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
                processing: "Procesando...",
                search: "Buscar:",
                lengthMenu: "Mostrar _MENU_ elementos",
                info: "Mostrando desde _START_ hasta _END_ de _TOTAL_ elementos",
                infoEmpty: "Mostrando desde 0 hasta 0 de 0 elementos",
                infoFiltered: "(filtrado de _MAX_ elementos en total)",
                infoPostFix: "",
                loadingRecords: "Cargando registros...",
                zeroRecords: "No se encontraron registros",
                emptyTable: "No hay datos disponibles en la tabla",
                paginate: {
                    first: "Primero",
                    previous: "Anterior",
                    next: "Siguiente",
                    last: "Último"
                },
                aria: {
                    sortAscending: ": Activar para ordenar la columna de manera ascendente",
                    sortDescending: ": Activar para ordenar la columna de manera descendente"
                }
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
        
        // Configurar eventos del widget
        setTimeout(() => {
            const widget = document.getElementById('altcha-widget');
            
            widget.addEventListener('statechange', (e) => {
                // Widget state changed
            });
            
            widget.addEventListener('verified', (e) => {
                // El widget devuelve un objeto con la propiedad 'payload'
                altchaSolutionValue = e.detail && e.detail.payload ? e.detail.payload : null;
            });
            
            widget.addEventListener('error', (e) => {
                console.error('Altcha widget error:', e.detail);
            });
        }, 100);
    });

    formReserve.addEventListener('submit', function(e) {
        e.preventDefault();
        const name = document.getElementById('reserver-name').value;
        const email = document.getElementById('reserver-email').value;
        
        // Obtener la solución de Altcha
        const altchaWidget = document.getElementById('altcha-widget');
        
        // Usar la solución almacenada primero, luego intentar obtenerla del widget
        let altchaSolution = altchaSolutionValue;
        
        if (!altchaSolution) {
            // Si no tenemos la solución almacenada, intentar obtenerla directamente
            if (altchaWidget.value) {
                altchaSolution = altchaWidget.value;
            } else {
                // Buscar en inputs hidden dentro del widget
                const hiddenInput = altchaWidget.querySelector('input[name="altcha"]');
                altchaSolution = hiddenInput ? hiddenInput.value : null;
            }
        }
        
        if (!altchaSolution) {
            alert('Please complete the captcha.');
            return;
        }
        
        fetch('/books/reserve/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                name: name,
                email: email,
                codes: Array.from(selectedBooks),
                altcha: altchaSolution
            })
        })
        .then(response => {
            // Verificar si la respuesta es JSON válida
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                return response.text().then(text => {
                    console.error('Server returned non-JSON response:', text);
                    throw new Error('Server returned invalid response');
                });
            }
            
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.message || 'Reservation error');
                });
            }
            return response.json();
        })
        .then(data => {
            // Limpiar todo
            reserveForm.style.display = 'none';
            selectedBooks.clear();
            reserveBtn.style.display = 'none';
            searchInput.value = '';
            resultsDiv.innerHTML = '';
            document.getElementById('reserver-name').value = '';
            document.getElementById('reserver-email').value = '';
            altchaWidget.reset();
            altchaSolutionValue = null; // Limpiar la solución almacenada
            // Mostrar mensaje de éxito
            messageDiv.textContent = document.getElementById('msg-success').textContent;
            messageDiv.style.display = 'block';
            setTimeout(() => {
                messageDiv.style.display = 'none';
            }, 4000);
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error processing reservation: ' + error.message);
            altchaWidget.reset();
            altchaSolutionValue = null; // Limpiar la solución almacenada
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