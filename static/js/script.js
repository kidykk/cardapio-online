document.addEventListener("DOMContentLoaded", () => {
 
  let carrinho = [];

  const btnAbrirModal = document.getElementById("but");
  const totalCarrinhoTopo = document.getElementById("total-carrinho");
  const modal = document.getElementById("modal-carrinho");
  const btnFechar = document.getElementById("btn-fechar");
  const listaProdutosModal = document.getElementById("lista-produtos");
  const valorTotalEl = document.getElementById("valor-total");

  const passoCarrinho = document.getElementById("passo-carrinho");
  const passoPagamento = document.getElementById("passo-pagamento");
  const passoSucesso = document.getElementById("passo-sucesso");

  const btnConfirmar = document.getElementById("btn-confirmar");
  const btnVoltar = document.getElementById("btn-voltar");
  const btnFinalizar = document.getElementById("btn-finalizar");
  const btnFecharFinal = document.getElementById("btn-fechar-final");

  const radiosPagamento = document.querySelectorAll('input[name="pagamento"]');
  const conteudoSucesso = document.getElementById("conteudo-sucesso");
  let timerInterval = null;
  let formaEscolhida = "";

  const cardsProdutos = document.querySelectorAll(".produto");
  const catalogo = [];

  cardsProdutos.forEach((card, index) => {
    const id = index + 1; // Produtos de 1 a 15
    const nome = card.querySelector("h3").textContent.trim();
    
    const paragrafos = card.querySelectorAll(".informacoes-produto p");
    const textoPreco = paragrafos[paragrafos.length - 1].textContent;
    const preco = parseFloat(textoPreco.replace("R$", "").replace(".", "").replace(",", ".").trim()) || 0;

    catalogo.push({ id, nome, preco });

    const btnAdicionar1 = document.getElementById(`adicionar-${id}`);
    const btnAumentar = document.getElementById(`aumentar-${id}`);
    const btnDiminuir = document.getElementById(`diminuir-${id}`);

    if (btnAdicionar1) {
      btnAdicionar1.addEventListener("click", () => atualizarQuantidadeProduto(id, 1));
    }
    if (btnAumentar) {
      btnAumentar.addEventListener("click", () => atualizarQuantidadeProduto(id, 1));
    }
    if (btnDiminuir) {
      btnDiminuir.addEventListener("click", () => atualizarQuantidadeProduto(id, -1));
    }
  });

  function atualizarQuantidadeProduto(id, delta) {
    const prodCatalogo = catalogo.find(p => p.id === id);
    if (!prodCatalogo) return;

    let itemCarrinho = carrinho.find(item => item.id === id);

    if (itemCarrinho) {
      itemCarrinho.qtd += delta;
      if (itemCarrinho.qtd <= 0) {
        carrinho = carrinho.filter(item => item.id !== id);
      }
    } else if (delta > 0) {
      carrinho.push({
        id: prodCatalogo.id,
        nome: prodCatalogo.nome,
        preco: prodCatalogo.preco,
        qtd: delta
      });
    }

    sincronizarInterface();
  }

  function sincronizarInterface() {
    catalogo.forEach(prod => {
      const item = carrinho.find(i => i.id === prod.id);
      const qtdAtual = item ? item.qtd : 0;

      const spanQtd = document.getElementById(`quantidade-${prod.id}`);
      if (spanQtd) spanQtd.textContent = qtdAtual;

      const btnAdd = document.getElementById(`adicionar-${prod.id}`);
   const controles = document.getElementById(`controles-${prod.id}`);
   if (btnAdd && controles) {
     if (qtdAtual > 0) {
       btnAdd.style.display = "none";
       controles.style.display = "inline-flex";
     } else {
       btnAdd.style.display = "inline-flex";
       controles.style.display = "none";
     }
   }
    });

    const totalItens = carrinho.reduce((acc, item) => acc + item.qtd, 0);
    if (totalCarrinhoTopo) {
      totalCarrinhoTopo.textContent = `Carrinho (${totalItens})`;
    }

    renderizarModalCarrinho();
  }

  function renderizarModalCarrinho() {
    listaProdutosModal.innerHTML = "";
    let totalPreco = 0;

    if (carrinho.length === 0) {
      listaProdutosModal.innerHTML = `<p style="text-align:center; color:#64748b; padding: 20px 0; font-size:14px;">Seu carrinho está vazio.</p>`;
      valorTotalEl.textContent = "0,00";
      return;
    }

    carrinho.forEach(item => {
      totalPreco += item.preco * item.qtd;

      const div = document.createElement("div");
      div.classList.add("item-carrinho");
      div.innerHTML = `
        <div>
          <span>${item.nome}</span><br>
          <small>R$ ${item.preco.toFixed(2).replace(".", ",")}</small>
        </div>
        <div class="controles">
          <button onclick="alterarQtdModal(${item.id}, -1)">-</button>
          <span>${item.qtd}</span>
          <button onclick="alterarQtdModal(${item.id}, 1)">+</button>
          <button class="btn-remover" onclick="removerItemModal(${item.id})">X</button>
        </div>
      `;
      listaProdutosModal.appendChild(div);
    });

    valorTotalEl.textContent = totalPreco.toFixed(2).replace(".", ",");
  }

  window.alterarQtdModal = function(id, delta) {
    atualizarQuantidadeProduto(id, delta);
  };

  window.removerItemModal = function(id) {
    carrinho = carrinho.filter(item => item.id !== id);
    sincronizarInterface();
  };

  btnAbrirModal.addEventListener("click", () => {
    renderizarModalCarrinho();
    passoCarrinho.classList.remove("oculto");
    passoPagamento.classList.add("oculto");
    passoSucesso.classList.add("oculto");
    modal.classList.remove("oculto");
    resetarFluxoPagamento();
  });

  btnFechar.addEventListener("click", () => {
    modal.classList.add("oculto");
    resetarFluxoPagamento();
  });

  btnConfirmar.addEventListener("click", () => {
    if (carrinho.length === 0) {
      alert("Adicione pelo menos um item do cardápio antes de confirmar!");
      return;
    }
    passoCarrinho.classList.add("oculto");
    passoPagamento.classList.remove("oculto");
    resetarFluxoPagamento();
  });

  btnVoltar.addEventListener("click", () => {
    passoPagamento.classList.add("oculto");
    passoCarrinho.classList.remove("oculto");
    resetarFluxoPagamento();
  });

  radiosPagamento.forEach(radio => {
    radio.addEventListener("change", (e) => {
      formaEscolhida = e.target.value;
      btnFinalizar.classList.remove("oculto");
    });
  });

  btnFinalizar.addEventListener("click", () => {
    passoPagamento.classList.add("oculto");
    passoSucesso.classList.remove("oculto");

    if (timerInterval) clearInterval(timerInterval);

    if (formaEscolhida === "pix") {
      conteudoSucesso.innerHTML = `
        <h2>Pagamento via Pix</h2>
        <div class="area-pix" style="margin-top: 10px;">
          <p>Aponte a câmera do seu celular para esse QR Code ou clique em "Copiar código" e cole no seu banco para efetuar o pagamento.</p>
          <div class="qr-falso">
            <svg viewBox="0 0 24 24" width="100" height="100" fill="#1e293b">
              <path d="M2 2h8v8H2V2zm2 2v4h4V4H4zm10-2h8v8h-8V2zm2 2v4h4V4h-4zM2 14h8v8H2v-8zm2 2v4h4v-4H4zm14 2h2v2h-2v-2zm-4-4h2v2h-2v-2zm4 0h2v2h-2v-2zm2 4h2v2h-2v-2zm-2 2h2v2h-2v-2zm2 2h2v2h-2v-2z"/>
            </svg>
          </div>
          <div class="timer-pix" id="timer-display">Tempo restante: 05:00</div>
          <div class="input-copia-container">
            <input type="text" id="codigo-pix" value="00020126580014br.gov.bcb.pix0136sashiminoku-pagamento-pedido-online" readonly>
            <button class="btn-copiar" id="btn-copiar">Copiar código</button>
          </div>
        </div>
      `;

      iniciarTimer(300);

      document.getElementById("btn-copiar").addEventListener("click", () => {
        const inputPix = document.getElementById("codigo-pix");
        inputPix.select();
        navigator.clipboard.writeText(inputPix.value);
        alert("Código Pix copiado com sucesso!");
      });

    } else if (formaEscolhida === "credito" || formaEscolhida === "debito") {
      const nomeCartao = formaEscolhida === "credito" ? "Cartão de Crédito" : "Cartão de Débito";
      conteudoSucesso.innerHTML = `
        <h2>${nomeCartao}</h2>
        <div class="form-cartao" style="margin-top: 10px;">
          <p style="font-size: 13px; font-weight: 600; color: #1e293b; margin-bottom: 4px;">Preencha os dados para concluir:</p>
          <input type="text" placeholder="Número do Cartão (ex: 0000 0000 0000 0000)" maxlength="19">
          <input type="text" placeholder="Nome impresso no Cartão">
          <div style="display: flex; gap: 8px;">
            <input type="text" placeholder="MM/AA" maxlength="5">
            <input type="text" placeholder="CVV" maxlength="4">
          </div>
        </div>
      `;
    }
  });

  btnFecharFinal.addEventListener("click", async () => {

    if (!formaEscolhida || carrinho.length === 0) {
        alert("Selecione uma forma de pagamento e adicione produtos.");
        return;
    }

    try {
        const resposta = await fetch("/api/pedidos", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                pagamento: formaEscolhida,
                itens: carrinho.map(item => ({
                    id: item.id,
                    qtd: item.qtd
                }))
            })
        });

        const resultado = await resposta.json();

        if (!resposta.ok) {
            alert(resultado.mensagem || "Não foi possível registrar o pedido.");
            return;
        }

        alert("Pedido #" + resultado.pedido_id + " registrado com sucesso!");

        carrinho = [];
        sincronizarInterface();
        modal.classList.add("oculto");
        resetarFluxoPagamento();

    } catch (erro) {
        alert("Erro ao enviar o pedido. Verifique sua conexão e tente novamente.");
    }
});

  function resetarFluxoPagamento() {
    radiosPagamento.forEach(el => el.checked = false);
    btnFinalizar.classList.add("oculto");
    formaEscolhida = "";
    conteudoSucesso.innerHTML = "";
    if (timerInterval) clearInterval(timerInterval);
  }

  function iniciarTimer(duracaoSegundos) {
    let tempo = duracaoSegundos;
    const display = document.getElementById("timer-display");
    
    timerInterval = setInterval(() => {
      let minutos = Math.floor(tempo / 60);
      let segundos = tempo % 60;

      minutos = minutos < 10 ? "0" + minutos : minutos;
      segundos = segundos < 10 ? "0" + segundos : segundos;

      if (display) {
        display.textContent = `Tempo restante: ${minutos}:${segundos}`;
      }

      if (--tempo < 0) {
        clearInterval(timerInterval);
        if (display) display.textContent = "QR Code expirado!";
      }
    }, 1000);
  }
});