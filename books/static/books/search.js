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
        console.log('renderResults called with:', books); // Debug
        
        if (!books || books.length === 0) {
            resultsDiv.innerHTML = '<div style="padding: 20px; text-align: center; color: #666;">No se encontraron resultados.</div>';
            return;
        }

        // Crear grilla visual de libros con imágenes de portada
        resultsDiv.innerHTML = '<div class="books-grid"></div>';
        const grid = resultsDiv.querySelector('.books-grid');
        
        books.forEach(book => {
            console.log('Processing book:', book); // Debug
            
            const bookCard = document.createElement('div');
            bookCard.className = `book-card-item ${book.is_available ? 'available' : 'unavailable'}`;
            
            // Crear imagen de portada
            const coverImageHtml = book.cover_image_url 
                ? `<img src="${book.cover_image_url}" alt="Portada de ${book.title}" style="width: 100%; height: 100%; object-fit: cover;">` 
                : '<div class="no-image">📚</div>';
                
            // Determinar clase del status para el badge
            const statusClass = book.status.toLowerCase().replace(/\s+/g, '');
            
            bookCard.innerHTML = `
                <div class="status-badge ${statusClass}">${book.status}</div>
                
                <div class="book-checkbox-container">
                    <input type="checkbox" class="book-check" data-code="${book.code}" ${book.is_available ? '' : 'disabled'}>
                </div>
                
                <div class="book-cover">
                    ${coverImageHtml}
                </div>
                
                <div class="book-info">
                    <div class="book-title" title="${book.title}">${book.title}</div>
                    <div class="book-authors">${book.authors}</div>
                    <div class="book-publisher">${book.publisher}</div>
                    <div class="book-details">
                        <span><strong>ISBN:</strong> ${book.isbn}</span>
                        <span><strong>Págs:</strong> ${book.pages}</span>
                    </div>
                    ${book.description ? `<div class="book-description" style="font-size: 0.8rem; color: #666; margin-top: 8px;">${book.description.substring(0, 100)}${book.description.length > 100 ? '...' : ''}</div>` : ''}
                </div>
                
                <div class="library-info">
                    <strong>${book.library}</strong><br>
                    ${book.address}
                </div>
            `;
            
            grid.appendChild(bookCard);
        });

        // Agregar event listeners para los checkboxes
        document.querySelectorAll('.book-check').forEach(cb => {
            cb.addEventListener('change', function() {
                if (this.checked) {
                    selectedBooks.add(this.dataset.code);
                } else {
                    selectedBooks.delete(this.dataset.code);
                }
                
                updateReserveButtonAndInfo();
            });
        });
    }
    
    function updateReserveButtonAndInfo() {
        if (selectedBooks.size > 0) {
            reserveBtn.style.display = 'block';
            
            // Agrupar libros seleccionados por biblioteca para mostrar información
            const selectedItems = Array.from(selectedBooks);
            const librariesInfo = {};
            
            // Buscar información de bibliotecas de los libros seleccionados
            document.querySelectorAll('.book-check:checked').forEach(checkbox => {
                const bookCard = checkbox.closest('.book-card-item');
                const libraryInfo = bookCard.querySelector('.library-info strong').textContent;
                
                if (!librariesInfo[libraryInfo]) {
                    librariesInfo[libraryInfo] = 0;
                }
                librariesInfo[libraryInfo]++;
            });
            
            // Actualizar el texto del botón con información de bibliotecas
            const libraryCount = Object.keys(librariesInfo).length;
            let buttonText = `Reservar ${selectedBooks.size} libro${selectedBooks.size > 1 ? 's' : ''}`;
            
            if (libraryCount > 1) {
                buttonText += ` (${libraryCount} bibliotecas)`;
                reserveBtn.innerHTML = `
                    ${buttonText}<br>
                    <small style="font-size: 0.8em; opacity: 0.9;">Se crearán ${libraryCount} reservas separadas</small>
                `;
                reserveBtn.style.height = 'auto';
                reserveBtn.style.padding = '12px 24px';
            } else {
                reserveBtn.textContent = buttonText;
                reserveBtn.style.height = '';
                reserveBtn.style.padding = '';
            }
        } else {
            reserveBtn.style.display = 'none';
        }
    }

    

    searchInput.addEventListener('input', function() {
        const query = searchInput.value;
        console.log('Searching for:', query); // Debug
        fetch(`/books/search/?q=${encodeURIComponent(query)}`)
            .then(response => {
                console.log('Response status:', response.status); // Debug
                return response.json();
            })
            .then(data => {
                console.log('Received data:', data); // Debug
                console.log('Number of results:', data.results ? data.results.length : 0); // Debug
                renderResults(data.results);
                selectedBooks.clear();
                reserveBtn.style.display = 'none';
                reserveForm.style.display = 'none';
            })
            .catch(error => {
                console.error('Error in search:', error); // Debug
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
            console.log('Reservation response:', data); // Debug
            
            // Limpiar formulario y selecciones
            reserveForm.style.display = 'none';
            selectedBooks.clear();
            reserveBtn.style.display = 'none';
            searchInput.value = '';
            resultsDiv.innerHTML = '';
            document.getElementById('reserver-name').value = '';
            document.getElementById('reserver-email').value = '';
            altchaWidget.reset();
            altchaSolutionValue = null; // Limpiar la solución almacenada
            
            // Crear mensaje detallado de reservas
            let successHTML = `<div style="background: #d4edda; color: #155724; padding: 15px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #c3e6cb;">`;
            successHTML += `<h4 style="margin: 0 0 10px 0; color: #155724;">✅ ${data.message}</h4>`;
            
            if (data.reservations && data.reservations.length > 0) {
                if (data.reservations.length > 1) {
                    successHTML += `<div style="margin-top: 10px;"><strong>Detalles de las reservas creadas:</strong></div>`;
                }
                
                data.reservations.forEach((reservation, index) => {
                    successHTML += `
                        <div style="background: rgba(255,255,255,0.7); padding: 10px; border-radius: 5px; margin: 8px 0; border-left: 4px solid #28a745;">
                            <strong>📍 ${reservation.library_name}</strong><br>
                            <small style="color: #666;">${reservation.library_address}</small><br>
                            <span style="color: #155724; font-weight: 500;">📚 ${reservation.items_count} libro${reservation.items_count > 1 ? 's' : ''} reservado${reservation.items_count > 1 ? 's' : ''}</span><br>
                            <small style="color: #666;">ID de reserva: #${reservation.reservation_id}</small>
                        </div>
                    `;
                });
                
                successHTML += `<div style="margin-top: 15px; font-style: italic; color: #0c5d2c;">
                    💡 Contacta con cada biblioteca por separado para organizar la recolección de tus libros.
                </div>`;
            }
            
            successHTML += `</div>`;
            
            // Mostrar el mensaje detallado
            messageDiv.innerHTML = successHTML;
            messageDiv.style.display = 'block';
            messageDiv.style.background = 'transparent';
            messageDiv.style.border = 'none';
            messageDiv.style.padding = '0';
            messageDiv.scrollIntoView({ behavior: 'smooth' });
            
            // Ocultar mensaje después de un tiempo más largo debido al contenido adicional
            setTimeout(() => {
                messageDiv.style.display = 'none';
            }, 8000);
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