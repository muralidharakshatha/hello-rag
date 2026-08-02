// Find the page elements that the chat interaction needs.
const form = document.querySelector("#chat-form");
const questionInput = document.querySelector("#question");
const messages = document.querySelector("#messages");
const sendButton = document.querySelector("#send-button");

// Add one safe text-only message to the conversation.
function addMessage(role, text, fact = "") {
  const article = document.createElement("article");
  article.className = `message ${role}-message`;

  if (role === "assistant") {
    const avatar = document.createElement("div");
    avatar.className = "avatar";
    avatar.textContent = "L";
    article.appendChild(avatar);
  }

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  const body = document.createElement("p");
  body.textContent = text;
  bubble.appendChild(body);

  if (fact) {
    const source = document.createElement("div");
    source.className = "source";
    source.textContent = `Retrieved fact: ${fact}`;
    bubble.appendChild(source);
  }

  article.appendChild(bubble);
  messages.appendChild(article);
  messages.scrollTop = messages.scrollHeight;
}

// Send one question to the Python RAG endpoint.
async function askQuestion(question) {
  addMessage("user", question);
  questionInput.value = "";
  sendButton.disabled = true;
  sendButton.textContent = "Thinking…";

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    const data = await response.json();

    if (!response.ok) throw new Error(data.error || "Something went wrong.");
    addMessage("assistant", data.answer, data.fact);
  } catch (error) {
    addMessage("assistant", error.message);
  } finally {
    sendButton.disabled = false;
    sendButton.textContent = "Send";
    questionInput.focus();
  }
}

// Submit typed questions without reloading the page.
form.addEventListener("submit", (event) => {
  event.preventDefault();
  const question = questionInput.value.trim();
  if (question) askQuestion(question);
});

// Let Enter send while Shift+Enter adds a new line.
questionInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    form.requestSubmit();
  }
});

// Fill and immediately send any suggested question the user clicks.
document.querySelectorAll("[data-question]").forEach((button) => {
  button.addEventListener("click", () => askQuestion(button.dataset.question));
});
