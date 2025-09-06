function verificaPassword() {
  const input = document.getElementById("password").value;
  const errore = document.getElementById("errore");

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
        window.location.href = "home.html";
      } else {
        errore.textContent = "❌ Password errata.";
      }
    })
    .catch(err => {
      errore.textContent = "❌ " + err.message;
      console.error("Errore login:", err);
    });
}
