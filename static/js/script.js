
// Seleciona o elemento que exibe a quantidade de produtos
const quantidade = document.getElementById("quantidade");

// Seleciona o indicador do carrinho no cabeçalho
const carrinho = document.getElementById("total-carrinho");

// Função responsável por atualizar o indicador do carrinho
function atualizarCarrinho() {
    // Obtém a quantidade atual selecionada no produto
    const valorAtual = Number(quantidade.textContent);

    // Atualiza o texto exibido no cabeçalho
    carrinho.textContent = `Carrinho (${valorAtual})`;
}

// Botão para adicionar uma unidade ao produto
document.getElementById("aumentar").addEventListener("click", function() {

    // Recupera a quantidade atual e adiciona uma unidade
    const valorAtual = Number(quantidade.textContent);
    quantidade.textContent = valorAtual + 1;

    // Atualiza o indicador do carrinho
    atualizarCarrinho();
});

// Botão para remover uma unidade do produto
document.getElementById("diminuir").addEventListener("click", function() {

    // Recupera a quantidade atual
    const valorAtual = Number(quantidade.textContent);

    // Verifica se a quantidade é maior que zero antes de remover
    if (valorAtual > 0) {
        quantidade.textContent = valorAtual - 1;
    }

    // Atualiza o indicador do carrinho
    atualizarCarrinho();
});