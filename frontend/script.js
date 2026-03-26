const API_BASE_URL = "";

const chatBox = document.getElementById("chat-box");
const startSessionBtn = document.getElementById("start-session-btn");
const resetBtn = document.getElementById("reset-btn");
const chatForm = document.getElementById("chat-form");
const messageInput = document.getElementById("message-input");
const sendBtn = document.getElementById("send-btn");
const statusText = document.getElementById("status-text");

let clientId = null;

function addMessage(text, sender = "bot") {
  const messageWrapper = document.createElement("div");
  messageWrapper.classList.add("message", sender);

  const bubble = document.createElement("div");
  bubble.classList.add("bubble");
  bubble.textContent = text;

  messageWrapper.appendChild(bubble);
  chatBox.appendChild(messageWrapper);
  chatBox.scrollTop = chatBox.scrollHeight;
}

function setChatEnabled(enabled) {
  messageInput.disabled = !enabled;
  sendBtn.disabled = !enabled;
}

async function createSession() {
  try {
    statusText.textContent = "Status: criando sessão...";

    const response = await fetch(`${API_BASE_URL}/api/session`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({})
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || data.error || "Erro ao criar sessão.");
    }

    clientId = data.client_id;
    localStorage.setItem("cardioia_client_id", clientId);

    setChatEnabled(true);
    statusText.textContent = "Status: sessão ativa";
    addMessage("Sessão iniciada com sucesso. Pode enviar sua mensagem.", "bot");
  } catch (error) {
    console.error(error);
    statusText.textContent = "Status: erro ao criar sessão";
    addMessage(`Erro ao criar sessão: ${error.message}`, "bot");
  }
}

async function sendMessage(message) {
  try {
    addMessage(message, "user");
    statusText.textContent = "Status: enviando mensagem...";

    const response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        client_id: clientId,
        message: message
      })
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || data.error || "Erro ao enviar mensagem.");
    }

    const messages = data.assistant_messages || [];

    if (messages.length === 0) {
      addMessage("O assistente não retornou uma resposta textual.", "bot");
    } else {
      messages.forEach((msg) => addMessage(msg, "bot"));
    }

    statusText.textContent = "Status: pronto";
  } catch (error) {
    console.error(error);
    statusText.textContent = "Status: erro ao enviar mensagem";
    addMessage(`Erro: ${error.message}`, "bot");
  }
}

async function resetConversation() {
  if (!clientId) {
    addMessage("Nenhuma sessão ativa para resetar.", "bot");
    return;
  }

  try {
    statusText.textContent = "Status: resetando conversa...";

    const response = await fetch(`${API_BASE_URL}/api/reset`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        client_id: clientId
      })
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || data.error || "Erro ao resetar conversa.");
    }

    chatBox.innerHTML = "";
    addMessage("Conversa resetada. Clique em 'Iniciar sessão' para começar novamente.", "bot");

    localStorage.removeItem("cardioia_client_id");
    clientId = null;
    setChatEnabled(false);
    statusText.textContent = "Status: sessão resetada";
  } catch (error) {
    console.error(error);
    statusText.textContent = "Status: erro ao resetar";
    addMessage(`Erro ao resetar: ${error.message}`, "bot");
  }
}

startSessionBtn.addEventListener("click", async () => {
  await createSession();
});

resetBtn.addEventListener("click", async () => {
  await resetConversation();
});

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const message = messageInput.value.trim();
  if (!message) return;

  messageInput.value = "";
  await sendMessage(message);
});

window.addEventListener("load", () => {
  localStorage.removeItem("cardioia_client_id");
  setChatEnabled(false);
  statusText.textContent = "Status: aguardando sessão";
});