const tg = window.Telegram.WebApp;
tg.expand();

const lista = document.getElementById("lista");

fetch("http://localhost:5000/api/iscritti")
  .then(res => res.json())
  .then(giocatori => {
    lista.innerHTML = "";
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
    console.error(err);
  });
