const tg = window.Telegram.WebApp;
tg.expand();

const lista = document.getElementById("lista");

fetch("http://localhost:5000/api/iscritti")
  .then(res => {
    if (!res.ok) {
      throw new Error(`HTTP error ${res.status}`);
    }
    return res.json();
  })
  .then(giocatori => {
    lista.innerHTML = ""; // pulizia
    if (!Array.isArray(giocatori)) {
      lista.innerHTML = "<p>⚠️ Nessun giocatore trovato.</p>";
      return;
    }

    giocatori.forEach(p => {
      const card = document.createElement("div");
      card.className = "card";
      card.innerHTML = `
        <div class="nome">${p.nome_player}</div>
        <div class="info">${p.th} | ${p.attacker_tag} | ${p.last_cwl_league || "Non assegnata"}</div>
      `;
      lista.appendChild(card);
    });
  })
  .catch(err => {
    lista.innerHTML = "<p>❌ Errore nel caricamento dei dati.</p>";
    console.error("Errore fetch JSON:", err);
  });
