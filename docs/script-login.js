// Funzione per verificare la password
function verificaPassword() {
  const input = document.getElementById("password").value;
  const errore = document.getElementById("errore");

  if (!input) {
    errore.textContent = "❌ Inserisci la password.";
    return;
  }

  // 🔗 Inserisci qui l'URL del tuo backend FastAPI 
  const BACKEND_URL = "https://tuo-dominio.it/api/login"; // ← cambia questo!

  fetch(BACKEND_URL, {
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
        window.location.href = "home.html"; // ✅ Accesso riuscito
      } else {
        errore.textContent = "❌ Password errata.";
      }
    })
    .catch(err => {
      errore.textContent = "❌ " + err.message;
      console.error("Errore login:", err);
    });
}


// vrsione senza backend per test locale
/*function verificaPassword() {
  const input = document.getElementById("password").value;
  const errore = document.getElementById("errore");

  if (!input) {
    errore.textContent = "❌ Inserisci la password.";
    return;
  }

  const PASSWORD_CORRETTA = "";

  if (input === PASSWORD_CORRETTA) {
    window.location.href = "home.html"; // ✅ Redirect simulato
  } else {
    errore.textContent = "❌ Password errata.";
  }
}*/


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
