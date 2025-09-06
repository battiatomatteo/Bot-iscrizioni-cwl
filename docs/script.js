const tg = window.Telegram.WebApp;
tg.expand();

function caricaGiocatori() {
  fetch("iscritti.json")
    .then(res => res.json())
    .then(data => {
      const lista = document.getElementById("lista");
      lista.innerHTML = "";
      const giocatori = data.lista_principale;
      giocatori.forEach(p => {
        const card = document.createElement("div");
        card.className = "card";
        card.innerHTML = `
          <div class="nome">${p.nome_player}</div>
          <div class="info">${p.th} | ${p.attacker_tag} | ${p.last_cwl_league || "Non assegnata"}</div>
        `;
        lista.appendChild(card);
      });
    });
}

function invia() {
  tg.sendData("Suddivisione inviata");
}

caricaGiocatori();
