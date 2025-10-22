document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('.add-item-form');
    const pageTitle = document.querySelector('.form-title');
    const submitButton = document.querySelector('.btn-submit');
    
    // Pega os parâmetros da URL
    const urlParams = new URLSearchParams(window.location.search);
    const editId = urlParams.get('editId'); // Procura por ?editId=... na URL
    const isEditMode = editId !== null; // Se encontrou um ID, estamos no modo de edição

    let allItems = JSON.parse(localStorage.getItem('estoqueItens')) || [];
    let itemToEdit = null;

    // --- MODO DE EDIÇÃO ---
    if (isEditMode) {
        pageTitle.textContent = 'Editar Item do Estoque'; // Muda o título da página
        submitButton.textContent = 'Salvar Alterações'; // Muda o texto do botão

        // Encontra o item que corresponde ao ID da URL
        itemToEdit = allItems.find(item => item.codigo === editId);

        if (itemToEdit) {
            // Preenche os campos do formulário com os dados do item
            document.getElementById('codigo').value = itemToEdit.codigo;
            document.getElementById('codigo').readOnly = true; // Torna o campo de código não-editável
            document.getElementById('quantidade').value = itemToEdit.quantidade;
            document.getElementById('endereco').value = itemToEdit.endereco;
            document.getElementById('tipo').value = itemToEdit.tipo;
            document.getElementById('marca').value = itemToEdit.marca;
            document.getElementById('maquina').value = itemToEdit.maquina;
            document.getElementById('descricao').value = itemToEdit.descricao;
        } else {
            alert("Erro: Item para edição não encontrado!");
        }
    }

    // --- LÓGICA PARA SALVAR (ADICIONAR OU EDITAR) ---
    form.addEventListener('submit', function(event) {
        event.preventDefault();

        // Coleta os dados do formulário
        const itemData = {
            codigo: document.getElementById('codigo').value,
            quantidade: document.getElementById('quantidade').value,
            endereco: document.getElementById('endereco').value,
            tipo: document.getElementById('tipo').value,
            marca: document.getElementById('marca').value,
            maquina: document.getElementById('maquina').value,
            descricao: document.getElementById('descricao').value
        };
        
        if (isEditMode) {
            // --- ATUALIZAR UM ITEM EXISTENTE ---
            const itemIndex = allItems.findIndex(item => item.codigo === editId);
            if (itemIndex !== -1) {
                allItems[itemIndex] = itemData; // Substitui o item antigo pelos novos dados
                localStorage.setItem('estoqueItens', JSON.stringify(allItems));
                alert('Item atualizado com sucesso!');
            }
        } else {
            // --- ADICIONAR UM NOVO ITEM ---
            // Verifica se o código do item já existe
            const itemExists = allItems.some(item => item.codigo === itemData.codigo);
            if (itemExists) {
                alert('Erro: Já existe um item com este código!');
                return; // Para a execução
            }

            allItems.push(itemData);
            localStorage.setItem('estoqueItens', JSON.stringify(allItems));
            alert('Item adicionado com sucesso!');
        }

        // Redireciona de volta para a página de estoque
        window.location.href = 'estoque.html';
    });
});