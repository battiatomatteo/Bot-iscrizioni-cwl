const tg = window.Telegram.WebApp;
tg.expand();

// Esempio statico: puoi sostituire con fetch da JSON
const giocatori = [
  { nome: "IL_POPE", th: "TH15", tag: "#ABC123", lega: "Champion League III" },
  { nome: "DARKSOUL", th: "TH14", tag: "#XYZ789", lega: "Master League I" },
  { nome: "SHADOW", th: "TH13", tag: "#LMN456", lega: "Non assegnata" }
];

const lista = document.getElementById("lista");

giocatori.forEach(p => {
  const card = document.createElement("div");
  card.className = "card";
  card.innerHTML = `
    <div class="nome">${p.nome}</div>
    <div class="info">${p.th} | ${p.tag} | ${p.lega}</div>
  `;
  lista.appendChild(card);
});

function invia() {
  const payload = {
    suddivisione: giocatori
  };
  tg.sendData(JSON.stringify(payload));
}
