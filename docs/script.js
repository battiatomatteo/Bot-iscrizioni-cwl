document.addEventListener("DOMContentLoaded", () => {
  const listaDiv = document.getElementById("lista");

  fetch("https://TUO_DOMINIO/api/iscritti") // ← cambia con il tuo dominio reale
    .then(res => res.json())
    .then(data => {
      if (Array.isArray(data)) {
        listaDiv.innerHTML = data.map(player => `
          <div class="iscritto">
            <strong>${player.nome_player}</strong> (${player.th})<br>
            🏷️ Tag: ${player.attacker_tag}<br>
            👤 Username: ${player.username}<br>
            🏆 Ultima CWL: ${player.last_cwl_league}
          </div>
          <hr>
        `).join("");
      } else {
        listaDiv.textContent = "⚠️ Nessun iscritto trovato.";
      }
    })
    .catch(err => {
      console.error("Errore nel caricamento:", err);
      listaDiv.textContent = "❌ Errore nel caricamento degli iscritti.";
    });
});

function invia() {
  alert("📤 Funzione di invio non ancora implementata.");
}
