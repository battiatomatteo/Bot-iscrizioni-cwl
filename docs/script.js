const tg = window.Telegram.WebApp;
tg.expand();

const CONFIG = {
  PASSWORD: "AdminAV1!"
};

function verificaPassword() {
  const input = document.getElementById("password").value;
  const errore = document.getElementById("errore");

  if (input === PASSWORD) {
    document.getElementById("login").style.display = "none";
    document.getElementById("app").style.display = "block";
    caricaGiocatori();
  } else {
    errore.textContent = "❌ Password errata.";
  }
}

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
