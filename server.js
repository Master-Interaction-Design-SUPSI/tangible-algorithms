const express = require("express");
const { WebSocketServer } = require("ws");
const http = require("http");
const { exec } = require("child_process");

const app = express();
const port = 3000;

// Servire i file statici dalla cartella 'public'
app.use(express.static("public"));

const server = http.createServer(app);
const wss = new WebSocketServer({ server });

wss.on("connection", (ws) => {
  console.log("Nuova connessione WebSocket");

  ws.on("message", (message) => {
    console.log("SOCKET: Ricevuto: %s", message);
    const { action, value, state } = JSON.parse(message);

    // Assumi che esista uno script Python denominato 'your_script.py' nella cartella principale
    const pythonCommand = `python3 script.py "${action}" "${value}" "${state}"`;

    exec(pythonCommand, (error, stdout, stderr) => {
      if (error) {
        console.error(
          `Errore durante l'esecuzione dello script Python: ${error}`
        );
        return ws.send(`Errore: ${error.message}`);
      }
      console.log(`stdout: ${stdout}`);
      ws.send(`Risultato: ${stdout}`);
    });
  });
});

server.listen(port, () => {
  console.log(`Server in ascolto su http://localhost:${port}`);
});
