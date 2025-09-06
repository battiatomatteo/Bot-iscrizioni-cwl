const tg = window.Telegram.WebApp;
tg.expand();

const PASSWORD_CORRETTA = CONFIG.PASSWORD;


function verificaPassword() {
  const input = document.getElementById("password").value;
  const errore = document.getElementById("errore");

  fetch("http://localhost:5000/api/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ password: input })
  })
    .then(res => {
      if (!res.ok) throw new Error("Password errata");
      return res.json();
    })
    .then(data => {
      if (data.success) {
        document.getElementById("login").style.display = "none";
        document.getElementById("app").style.display = "block";
        caricaGiocatori();
      }
    })
    .catch(err => {
      errore.textContent = "❌ Password errata.";
      console.error(err);
    });
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
