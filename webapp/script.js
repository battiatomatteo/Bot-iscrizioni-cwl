const tg = window.Telegram.WebApp;
tg.expand();

function invia() {
  const dati = { lista1: [...], lista2: [...] }; // esempio
  tg.sendData(JSON.stringify(dati));
}
