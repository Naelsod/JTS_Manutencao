document.addEventListener('DOMContentLoaded', function() {
    // --- SELETORES DOS ELEMENTOS ---
    const stockList = document.querySelector('.stock-list');
    const filterOptions = document.querySelector('.filter-options');
    // NOVO: Seletores da barra de pesquisa
    const searchInput = document.querySelector('.search-bar input[type="text"]');
    const searchButton = document.querySelector('.search-bar .btn-buscar');

    // --- VERIFICAÇÃO INICIAL ---
    if (!stockList) {
        console.error("ERRO: A div com a classe '.stock-list' não foi encontrada!");
        return;
    }
    if (!filterOptions) {
        console.error("ERRO: A div com a classe '.filter-options' não foi encontrada!");
        return;
    }
    // NOVO: Verificação dos elementos de pesquisa
    if (!searchInput || !searchButton) {
        console.error("ERRO: Elementos da barra de pesquisa não foram encontrados!");
        return;
    }

    let allItems = []; // Array global para armazenar todos os itens do localStorage

    // --- FUNÇÃO PRINCIPAL DE RENDERIZAÇÃO ---
    function renderStockItems(itemsToRender) {
        if (itemsToRender.length === 0) {
            stockList.innerHTML = '<p class="empty-stock-message">Nenhum item encontrado.</p>';
        } else {
            stockList.innerHTML = ''; 
        }

        itemsToRender.forEach(item => {
            let iconClass = 'fa-solid fa-box';
            if (item.tipo === 'oleo') iconClass = 'fa-solid fa-oil-can';
            if (item.tipo === 'peca') iconClass = 'fa-solid fa-gear';
            if (item.tipo === 'filtro') iconClass = 'fa-solid fa-filter';
            if (item.tipo === 'cabo') iconClass = 'fa-solid fa-plug';

            const tituloDescricao = (item.descricao || 'Item').split(' ')[0].toUpperCase();

            const itemHtml = `
                <div class="stock-item">
                    <span class="item-cod">${item.codigo || '#N/D'}</span>
                    <span class="item-desc">${tituloDescricao}</span>
                    <span class="item-tipo"><i class="${iconClass}"></i></span>
                    <div class="item-quant">
                        <button class="quant-btn" data-action="decrement" data-item-id="${item.codigo}">-</button>
                        <span>${item.quantidade || 0}</span>
                        <button class="quant-btn" data-action="increment" data-item-id="${item.codigo}">+</button>
                    </div>
                    <button class="expand-btn"><i class="fa-solid fa-chevron-down"></i></button>
                    
                    <div class="item-details">
                        <div class="details-grid">
                            <strong>ENDEREÇO:</strong>   <span>${item.endereco || 'Não informado'}</span>
                            <strong>DESCRIÇÃO:</strong>  <span>${item.descricao || 'Não informado'}</span>
                            <strong>MARCA:</strong>       <span>${item.marca || 'Não informado'}</span>
                            <strong>MÁQUINA:</strong>    <span>${item.maquina || 'Não informado'}</span>
                        </div>
                        <div class="details-actions">
                            <a href="#" class="btn-edit" data-item-id="${item.codigo}">EDITAR</a>
                            <button class="icon-btn btn-delete" data-item-id="${item.codigo}"><i class="fa-solid fa-trash"></i></button>
                        </div>
                    </div>
                </div>
            `;
            stockList.innerHTML += itemHtml;
        });

        // Anexa todos os "ouvintes" aos novos botões
        attachExpandCollapseListeners();
        attachQuantityButtonsListeners();
        attachDeleteButtonsListeners();
        attachEditButtonsListeners();
    }

    // --- FUNÇÕES DE "OUVINTE" (attach...) ---
    // (Estas funções permanecem exatamente as mesmas de antes)
    function attachExpandCollapseListeners() { /* ...código idêntico... */ 
        const expandButtons = document.querySelectorAll('.expand-btn');
        expandButtons.forEach(button => {
            button.removeEventListener('click', handleExpandCollapse); 
            button.addEventListener('click', handleExpandCollapse);
        });
    }
    function attachQuantityButtonsListeners() { /* ...código idêntico... */ 
        const quantityButtons = document.querySelectorAll('.item-quant .quant-btn');
        quantityButtons.forEach(button => {
            button.removeEventListener('click', handleQuantityChange); 
            button.addEventListener('click', handleQuantityChange);
        });
    }
    function attachDeleteButtonsListeners() { /* ...código idêntico... */ 
        const deleteButtons = document.querySelectorAll('.btn-delete');
        deleteButtons.forEach(button => {
            button.removeEventListener('click', handleDeleteItem);
            button.addEventListener('click', handleDeleteItem);
        });
    }
    function attachEditButtonsListeners() { /* ...código idêntico... */ 
        const editButtons = document.querySelectorAll('.btn-edit');
        editButtons.forEach(button => {
            button.removeEventListener('click', handleEditItem);
            button.addEventListener('click', handleEditItem);
        });
    }


    // --- FUNÇÕES DE AÇÃO (handle...) ---
    // (Estas funções permanecem exatamente as mesmas de antes)
    function handleExpandCollapse() { /* ...código idêntico... */ 
        const stockItem = this.closest('.stock-item');
        stockItem.classList.toggle('expanded');
        const icon = this.querySelector('i');
        if (stockItem.classList.contains('expanded')) {
            icon.classList.remove('fa-chevron-down');
            icon.classList.add('fa-chevron-up');
        } else {
            icon.classList.remove('fa-chevron-up');
            icon.classList.add('fa-chevron-down');
        }
    }
    function handleQuantityChange() { /* ...código idêntico... */ 
        const action = this.dataset.action; 
        const itemId = this.dataset.itemId;
        let itemIndex = allItems.findIndex(item => item.codigo === itemId);

        if (itemIndex !== -1) {
            let currentQuantity = parseInt(allItems[itemIndex].quantidade);
            if (action === 'increment') {
                currentQuantity++;
            } else if (action === 'decrement' && currentQuantity > 0) {
                currentQuantity--;
            }
            allItems[itemIndex].quantidade = currentQuantity.toString();
            localStorage.setItem('estoqueItens', JSON.stringify(allItems));
            applyFilters(); 
        }
    }
    function handleDeleteItem() { /* ...código idêntico... */ 
        const itemIdToDelete = this.dataset.itemId;
        if (confirm(`Tem certeza que deseja excluir o item com código ${itemIdToDelete}?`)) {
            allItems = allItems.filter(item => item.codigo !== itemIdToDelete);
            localStorage.setItem('estoqueItens', JSON.stringify(allItems));
            applyFilters();
            alert('Item excluído com sucesso!');
        }
    }
    function handleEditItem(event) { /* ...código idêntico... */ 
        event.preventDefault(); 
        const itemId = this.dataset.itemId;
        console.log(`CLICOU EM EDITAR! ID do item: ${itemId}. Redirecionando...`);
        window.location.href = `/adc.html?editId=${itemId}`;
    }


    // --- LÓGICA DE FILTRAGEM E PESQUISA ---

    // 1. OUVINTES DE EVENTO (checkboxes e pesquisa)
    filterOptions.addEventListener('change', function(event) {
        if (event.target.type !== 'checkbox' || event.target.name !== 'filter-type') {
            return;
        }
        // (O código de lógica dos checkboxes permanece o mesmo de antes)
        const changedValue = event.target.value;
        const showAllCheckbox = filterOptions.querySelector('input[value="all"]');
        const otherCheckboxes = filterOptions.querySelectorAll('input[name="filter-type"]:not([value="all"])');

        if (changedValue === 'all') {
            otherCheckboxes.forEach(cb => {
                cb.checked = event.target.checked;
            });
        } else {
            if (!event.target.checked) {
                showAllCheckbox.checked = false;
            } else {
                const allOthersChecked = Array.from(otherCheckboxes).every(cb => cb.checked);
                if (allOthersChecked) {
                    showAllCheckbox.checked = true;
                }
            }
        }
        applyFilters(); // Chama a função mestre
    });

    // NOVO: Ouvintes para a pesquisa
    // Chama o filtro ao clicar no botão "Buscar"
    searchButton.addEventListener('click', function() {
        applyFilters();
    });
    // Chama o filtro em tempo real, enquanto o usuário digita
    searchInput.addEventListener('input', function() {
        applyFilters();
    });


    // 2. FUNÇÃO MESTRE QUE APLICA FILTROS E PESQUISA (MODIFICADA)
    function applyFilters() {
        
        // --- ETAPA 1: FILTRAGEM POR CHECKBOX (código anterior) ---
        const showAllCheckbox = filterOptions.querySelector('input[value="all"]');
        const activeFilters = Array.from(filterOptions.querySelectorAll('input[name="filter-type"]:checked:not([value="all"])'))
                                 .map(cb => cb.value);

        let itemsToShow;

        if (showAllCheckbox.checked) {
            itemsToShow = allItems;
        } else { 
            itemsToShow = allItems.filter(item => activeFilters.includes(item.tipo));
        }

        // --- ETAPA 2: FILTRAGEM POR PESQUISA (NOVO) ---
        const searchTerm = searchInput.value.toLowerCase().trim();

        if (searchTerm.length > 0) {
            // Filtra a lista *que já foi filtrada pelos checkboxes*
            itemsToShow = itemsToShow.filter(item => {
                // Procura o termo em múltiplos campos do item
                // Usamos `|| ''` para evitar erros caso um campo seja nulo
                return (item.codigo || '').toLowerCase().includes(searchTerm) ||
                       (item.descricao || '').toLowerCase().includes(searchTerm) ||
                       (item.marca || '').toLowerCase().includes(searchTerm) ||
                       (item.maquina || '').toLowerCase().includes(searchTerm) ||
                       (item.endereco || '').toLowerCase().includes(searchTerm);
            });
        }
        
        // --- DEBUG (Opcional, mas útil) ---
        console.log("Filtros ativos:", activeFilters);
        console.log("Termo de pesquisa:", searchTerm);
        console.log("Itens para mostrar:", itemsToShow);
        
        // --- ETAPA 3: RENDERIZAR O RESULTADO FINAL ---
        renderStockItems(itemsToShow);
    }

    // --- CARGA INICIAL ---
    try {
        const itensJSON = localStorage.getItem('estoqueItens');
        allItems = JSON.parse(itensJSON) || [];
        
        // Na primeira carga, marca todos os checkboxes (incluindo "Mostrar Tudo")
        filterOptions.querySelectorAll('input[type="checkbox"]').forEach(cb => {
            cb.checked = true;
        });
        
        applyFilters(); // Renderiza todos os itens inicialmente
    } catch (error) {
        console.error("Erro ao carregar itens do localStorage:", error);
        stockList.innerHTML = '<p class="error-message">Erro ao carregar o estoque.</p>';
    }
});