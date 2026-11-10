document.getElementById("quantidade").textContent = 0;

document.getElementById("aumentar").addEventListener("click", function() {

    let quantidade = document.getElementById("quantidade");

    let valorAtual = Number(quantidade.textContent);

    quantidade.textContent = valorAtual + 1;

    
});

document.getElementById("diminuir").addEventListener("click", function() {

    let quantidade = document.getElementById("quantidade");

    let valorAtual = Number(quantidade.textContent);

    if (valorAtual > 0) {
        quantidade.textContent = valorAtual - 1;
    }
});