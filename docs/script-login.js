// Funzione per verificare la password
function verificaPassword() {
  const input = document.getElementById("password").value;
  const errore = document.getElementById("errore");

  // Controllo input vuoto
  if (!input) {
    errore.textContent = "❌ Inserisci la password.";
    return;
  }

  // Invio richiesta al backend
  fetch("http://localhost:5000/api/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ password: input })
  })
    .then(async res => {
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.message || "Password errata");
      }
      return res.json();
    })
    .then(data => {
      if (data.success) {
        window.location.href = "home.html"; // ✅ Redirect alla home
      } else {
        errore.textContent = "❌ Password errata.";
      }
    })
    .catch(err => {
      errore.textContent = "❌ " + err.message;
      console.error("Errore login:", err);
    });
}

// Funzione per mostrare/nascondere la password
document.getElementById("togglePassword").addEventListener("click", () => {
  const input = document.getElementById("password");
  const toggle = document.getElementById("togglePassword");

  if (input.type === "password") {
    input.type = "text";
    toggle.textContent = "🙈";
  } else {
    input.type = "password";
    toggle.textContent = "👁️";
  }
});
