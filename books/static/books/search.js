// Logging inmediato para verificar que el script se carga
console.log('=== SEARCH SCRIPT LOADING ===');

document.addEventListener('DOMContentLoaded', function() {
    console.log('=== DOM CONTENT LOADED ===');
    
    // Variables globales
    let selectedBooks = [];
    let searchTimeout;
    let altchaSolutionValue = null; // Variable para almacenar la solución ALTCHA

    
    
    // Elementos del DOM
    const searchInput = document.getElementById('search');
    const resultsContainer = document.getElementById('results');
    const resultsSection = document.getElementById('results-section');
    const noResults = document.getElementById('no-results');
    const reserveBtn = document.getElementById('reserve-btn');
    const reserveForm = document.getElementById('reserve-form');
    const formReserve = document.getElementById('form-reserve');
    const msgSuccess = document.getElementById('msg-success');
    const selectedCount = document.getElementById('selected-count');
    const cancelReservationBtn = document.getElementById('cancel-reservation');

    // Verificar que los elementos existen
    console.log('=== ELEMENTS CHECK ===', {
        searchInput: !!searchInput,
        resultsContainer: !!resultsContainer,
        resultsSection: !!resultsSection,
        noResults: !!noResults
    });

    // Event Listeners con verificación
    if (searchInput) {
        console.log('=== ADDING SEARCH LISTENERS ===');
        
        searchInput.addEventListener('input', function() {
            console.log('INPUT EVENT:', this.value);
            handleSearch();
        });
        
        searchInput.addEventListener('keyup', function() {
            console.log('KEYUP EVENT:', this.value);
            handleSearch();
        });
        
        // Test inmediato
        console.log('Search input value on load:', searchInput.value);
    } else {
        console.error('=== SEARCH INPUT NOT FOUND ===');
    }
    
    if (reserveBtn) {
        reserveBtn.addEventListener('click', showReservationForm);
    }
    if (formReserve) {
        formReserve.addEventListener('submit', handleReservation);
    }
    if (cancelReservationBtn) {
        cancelReservationBtn.addEventListener('click', hideReservationForm);
    }

    // Manejar botones de reserva individual del carrusel
    document.querySelectorAll('.reserve-single-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const code = this.dataset.code;
            const title = this.dataset.title;
            selectedBooks = [code];
            updateSelectedCount();
            showReservationForm();
        });
    });

    // Función de búsqueda con debounce mejorada
    function handleSearch() {
        if (!searchInput) {
            console.error('Search input not found');
            return;
        }
        
        const query = searchInput.value.trim();
        console.log('Handling search for:', query);
        
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            if (query.length >= 2) {
                console.log('Executing search for:', query);
                searchBooks(query);
            } else if (query.length === 0) {
                console.log('Clearing results');
                hideResults();
            }
        }, 300);
    }

    // Buscar libros con logging mejorado
    function searchBooks(query) {
        console.log('=== SEARCH BOOKS START ===', query);
        
        showLoading();
        
        const url = `/books/search/?q=${encodeURIComponent(query)}`;
        console.log('Request URL:', url);
        
        fetch(url)
            .then(response => {
                console.log('Response received:', response.status, response.statusText);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('=== SEARCH SUCCESS ===');
                console.log('Response data:', data);
                console.log('Results count:', data.results?.length || 0);
                hideLoading();
                displayResults(data.results || []);
            })
            .catch(error => {
                console.error('=== SEARCH ERROR ===');
                console.error('Error details:', error);
                hideLoading();
                showError('Error al buscar libros: ' + error.message);
            });
    }

    // Mostrar resultados como tarjetas con logging mejorado
    function displayResults(results) {
        console.log('Displaying results:', results?.length || 0, 'items');
        
        if (!resultsContainer || !resultsSection) {
            console.error('Results containers not found');
            return;
        }
        
        if (!results || results.length === 0) {
            showNoResults();
            return;
        }

        resultsSection.style.display = 'block';
        noResults.style.display = 'none';
        resultsContainer.innerHTML = '';
        
        console.log('Creating cards for results...');
        results.forEach((book, index) => {
            const bookCard = createBookCard(book, index);
            resultsContainer.appendChild(bookCard);
        });

        // Animar la aparición de las tarjetas
        setTimeout(() => {
            document.querySelectorAll('.book-card-result').forEach((card, index) => {
                setTimeout(() => {
                    card.style.opacity = '1';
                    card.style.transform = 'translateY(0)';
                }, index * 100);
            });
        }, 50);
        
        console.log('Results displayed successfully');
    }

    // Crear tarjeta de libro
    function createBookCard(book, index) {
        const col = document.createElement('div');
        col.className = 'col-md-6 col-lg-4';

        const availabilityBadge = book.is_available ? 
            '<span class="badge bg-success availability-badge">Disponible</span>' :
            '<span class="badge bg-danger availability-badge">No disponible</span>';

        const coverImage = book.cover_image_url ? 
            `<img src="${book.cover_image_url}" alt="${book.title}" class="book-cover-result">` :
            '<div class="book-placeholder-small"><i class="fas fa-book"></i></div>';

        const tagsHtml = book.tags && book.tags.length > 0 ? 
            `<div class="book-tags">
                ${book.tags.map(tag => `<span class="badge bg-secondary">${tag}</span>`).join('')}
            </div>` : '';

        const checkboxHtml = book.is_available ? 
            `<input type="checkbox" class="form-check-input book-select-checkbox" 
                    data-code="${book.code}" data-title="${book.title}">` : '';

        col.innerHTML = `
            <div class="book-card-result ${!book.is_available ? 'unavailable' : ''}" 
                 style="opacity: 0; transform: translateY(20px);">
                ${checkboxHtml}
                ${availabilityBadge}
                <div class="position-relative">
                    ${coverImage}
                </div>
                <div class="book-card-body">
                    <h6 class="book-title">${book.title}</h6>
                    <p class="book-author">
                        <i class="fas fa-user me-1"></i>${book.authors}
                        ${book.publication_date ? `<span class="ms-2"><i class="fas fa-calendar me-1"></i>${book.publication_date}</span>` : ''}
                    </p>
                    ${book.illustrators ? `<p class="book-illustrator">
                        <i class="fas fa-paint-brush me-1"></i>Ilustrador: ${book.illustrators}
                    </p>` : ''}
                    <p class="book-library">
                        <i class="fas fa-map-marker-alt me-1"></i>${book.library_name}, ${book.library_city}
                    </p>
                    <p class="book-publisher">
                        <i class="fas fa-building me-1"></i>${book.publisher}
                    </p>
                    ${book.description ? `<p class="book-description">${truncateText(book.description, 100)}</p>` : ''}
                    ${tagsHtml}
                    <div class="d-flex justify-content-between align-items-center">
                        <small class="text-muted">
                            <i class="fas fa-barcode me-1"></i>${book.isbn}
                        </small>
                        ${book.is_available ? 
                            `<button class="btn btn-outline-primary btn-sm reserve-single-btn" 
                                     data-code="${book.code}" data-title="${book.title}">
                                <i class="fas fa-bookmark me-1"></i>Reservar
                            </button>` : 
                            '<span class="text-danger small"><i class="fas fa-times me-1"></i>No disponible</span>'
                        }
                    </div>
                </div>
            </div>
        `;

        // Agregar event listeners
        const checkbox = col.querySelector('.book-select-checkbox');
        if (checkbox) {
            checkbox.addEventListener('change', handleBookSelection);
        }

        const reserveSingleBtn = col.querySelector('.reserve-single-btn');
        if (reserveSingleBtn) {
            reserveSingleBtn.addEventListener('click', function() {
                selectedBooks = [this.dataset.code];
                updateSelectedCount();
                showReservationForm();
            });
        }

        return col;
    }

    // Manejar selección de libros
    function handleBookSelection() {
        const selectedCheckboxes = document.querySelectorAll('.book-select-checkbox:checked');
        selectedBooks = Array.from(selectedCheckboxes).map(cb => cb.dataset.code);
        
        // Actualizar estilos visuales
        document.querySelectorAll('.book-card-result').forEach(card => {
            const checkbox = card.querySelector('.book-select-checkbox');
            if (checkbox && checkbox.checked) {
                card.classList.add('selected');
            } else {
                card.classList.remove('selected');
            }
        });

        updateSelectedCount();
        toggleReserveButton();
    }

    // Actualizar contador de seleccionados
    function updateSelectedCount() {
        if (selectedCount) {
            selectedCount.textContent = selectedBooks.length;
            selectedCount.style.animation = 'pulse 0.3s ease-in-out';
            setTimeout(() => {
                selectedCount.style.animation = '';
            }, 300);
        }
    }

    // Mostrar/ocultar botón de reserva
    function toggleReserveButton() {
        if (selectedBooks.length > 0) {
            reserveBtn.style.display = 'inline-block';
            reserveBtn.innerHTML = `
                <i class="fas fa-bookmark me-2"></i>Reservar libros seleccionados
                <span id="selected-count" class="badge bg-light text-dark ms-2">${selectedBooks.length}</span>
            `;
        } else {
            reserveBtn.style.display = 'none';
        }
    }

    // Mostrar formulario de reserva
    function showReservationForm() {
        if (selectedBooks.length === 0) {
            alert('Por favor selecciona al menos un libro para reservar.');
            return;
        }

        reserveForm.style.display = 'block';
        reserveForm.scrollIntoView({ behavior: 'smooth' });
        
        // Reset form
        document.getElementById('reserver-name').value = '';
        document.getElementById('reserver-email').value = '';
        
        // Reset Altcha widget y variable
        const altchaWidget = document.getElementById('altcha-widget');
        if (altchaWidget) {
            altchaWidget.reset();
            altchaSolutionValue = null; // Limpiar la solución almacenada
            
            // Configurar eventos del widget ALTCHA
            setTimeout(() => {
                altchaWidget.addEventListener('verified', (e) => {
                    // Almacenar la solución cuando el widget es verificado
                    altchaSolutionValue = e.detail && e.detail.payload ? e.detail.payload : null;
                    console.log('ALTCHA verified, solution stored:', !!altchaSolutionValue);
                });
                
                altchaWidget.addEventListener('error', (e) => {
                    console.error('Altcha widget error:', e.detail);
                    altchaSolutionValue = null;
                });
                
                altchaWidget.addEventListener('reset', (e) => {
                    altchaSolutionValue = null;
                    console.log('ALTCHA reset, solution cleared');
                });
            }, 100);
        }
    }

    // Ocultar formulario de reserva
    function hideReservationForm() {
        reserveForm.style.display = 'none';
        
        // Limpiar selecciones
        selectedBooks = [];
        document.querySelectorAll('.book-select-checkbox:checked').forEach(cb => {
            cb.checked = false;
        });
        document.querySelectorAll('.book-card-result.selected').forEach(card => {
            card.classList.remove('selected');
        });
        
        // Limpiar ALTCHA
        const altchaWidget = document.getElementById('altcha-widget');
        if (altchaWidget) {
            altchaWidget.reset();
        }
        altchaSolutionValue = null;
        
        updateSelectedCount();
        toggleReserveButton();
    }

    // Manejar envío de reserva
    function handleReservation(e) {
        e.preventDefault();
        
        const name = document.getElementById('reserver-name').value.trim();
        const email = document.getElementById('reserver-email').value.trim();
        
        if (!name || !email) {
            alert('Por favor completa nombre y email.');
            return;
        }

        // Verificar que el captcha ALTCHA esté completado
        if (!altchaSolutionValue) {
            alert('Por favor completa el captcha de verificación.');
            return;
        }

        // Deshabilitar botón durante el envío
        const submitBtn = formReserve.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Procesando...';

        const reservationData = {
            name: name,
            email: email,
            codes: selectedBooks,
            altcha: altchaSolutionValue
        };

        fetch('/books/reserve/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify(reservationData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                showSuccessMessage(data.message);
                hideReservationForm();
                
                // Actualizar estado de libros reservados
                selectedBooks.forEach(code => {
                    const checkbox = document.querySelector(`[data-code="${code}"]`);
                    if (checkbox) {
                        const card = checkbox.closest('.book-card-result');
                        card.classList.add('unavailable');
                        checkbox.disabled = true;
                        checkbox.checked = false;
                        
                        // Actualizar badge y botón
                        const badge = card.querySelector('.availability-badge');
                        const btn = card.querySelector('.reserve-single-btn');
                        if (badge) badge.innerHTML = '<span class="badge bg-warning">Reservado</span>';
                        if (btn) btn.style.display = 'none';
                    }
                });
                
                selectedBooks = [];
            } else {
                throw new Error(data.error || 'Error desconocido');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error al procesar la reserva: ' + (error.message || 'Inténtalo de nuevo.'));
            
            // En caso de error, limpiar ALTCHA también
            const altchaWidget = document.getElementById('altcha-widget');
            if (altchaWidget) {
                altchaWidget.reset();
            }
            altchaSolutionValue = null;
        })
        .finally(() => {
            // Rehabilitar botón
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalText;
        });
    }

    // Funciones auxiliares
    function truncateText(text, maxLength) {
        if (text.length <= maxLength) return text;
        return text.substr(0, maxLength) + '...';
    }

    function showNoResults() {
        console.log('Showing no results message');
        if (resultsSection && noResults && resultsContainer) {
            resultsSection.style.display = 'block';
            noResults.style.display = 'block';
            resultsContainer.innerHTML = '';
        }
    }

    function hideResults() {
        console.log('Hiding results');
        if (resultsSection) {
            resultsSection.style.display = 'none';
        }
        selectedBooks = [];
        updateSelectedCount();
        if (reserveBtn) {
            reserveBtn.style.display = 'none';
        }
    }

    function showLoading() {
        console.log('=== SHOWING LOADING ===');
        if (resultsContainer && resultsSection) {
            resultsContainer.innerHTML = `
                <div class="col-12 text-center py-5">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Buscando...</span>
                    </div>
                    <p class="mt-3 text-muted">Buscando libros...</p>
                </div>
            `;
            resultsSection.style.display = 'block';
        }
    }

    function hideLoading() {
        console.log('=== HIDING LOADING ===');
        // La función displayResults se encarga de limpiar el loading
    }

    function showError(message) {
        console.log('=== SHOWING ERROR ===', message);
        if (resultsContainer) {
            resultsContainer.innerHTML = `
                <div class="col-12">
                    <div class="alert alert-danger text-center" role="alert">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        ${message}
                    </div>
                </div>
            `;
        }
    }

    function showSuccessMessage(message) {
        msgSuccess.style.display = 'block';
        msgSuccess.innerHTML = `
            <i class="fas fa-check-circle fa-2x me-3"></i>
            <strong>¡Reserva exitosa!</strong>
            <div class="mt-2">${message}</div>
        `;
        msgSuccess.scrollIntoView({ behavior: 'smooth' });
        
        // Ocultar después de 8 segundos
        setTimeout(() => {
            msgSuccess.style.display = 'none';
        }, 8000);
    }

    function getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }
    
    // Funciones para testing manual
    window.testSearch = function(query) {
        console.log('=== MANUAL TEST SEARCH ===', query);
        if (searchInput) {
            searchInput.value = query;
            handleSearch();
        } else {
            console.error('Search input not found for test');
        }
    };
    
    window.testDirectSearch = function(query) {
        console.log('=== DIRECT SEARCH TEST ===', query);
        searchBooks(query);
    };
    
    // Logging final
    console.log('=== SEARCH SCRIPT FULLY LOADED ===');
    console.log('Test functions available: testSearch(query), testDirectSearch(query)');

   

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

    // Event listener duplicado eliminado - ahora se maneja correctamente en showReservationForm

    // Event listener duplicado eliminado - se maneja en handleReservation función

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