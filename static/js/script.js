setInterval(atualizarRelogio, 1000);
atualizarRelogio();

const hoje = new Date();

document.getElementById("dataAtual").innerHTML =
    hoje.toLocaleDateString('pt-BR');