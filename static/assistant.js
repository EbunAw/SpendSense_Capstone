const API_BASE = "http://127.0.0.1:8000";

const chatMessages = document.getElementById("chat-messages");
const assistantForm = document.getElementById("assistant-form");
const questionInput = document.getElementById("assistant-question");
const submitButton = document.getElementById("assistant-submit");

function addMessage(role, text) {
    const messageElement = document.createElement("div");
    messageElement.className = `chat-message ${role}`;

    const paragraph = document.createElement("p");
    paragraph.textContent = text;

    messageElement.appendChild(paragraph);
    chatMessages.appendChild(messageElement);

    chatMessages.scrollTop = chatMessages.scrollHeight;

    return messageElement;
}

function addSources(messageElement, sources) {
    if (!sources || sources.length === 0) {
        return;
    }

    const sourcesContainer = document.createElement("div");
    sourcesContainer.className = "chat-sources";

    const heading = document.createElement("strong");
    heading.textContent = "Sources";
    sourcesContainer.appendChild(heading);

    const sourceList = document.createElement("ul");

    sources.forEach((source) => {
        const listItem = document.createElement("li");

        listItem.textContent =
            source.source ||
            source.filename ||
            source.title ||
            "Financial knowledge base";

        sourceList.appendChild(listItem);
    });

    sourcesContainer.appendChild(sourceList);
    messageElement.appendChild(sourcesContainer);
}

assistantForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const question = questionInput.value.trim();

    if (!question) {
        return;
    }

    addMessage("user", question);

    questionInput.value = "";
    submitButton.disabled = true;
    submitButton.textContent = "Thinking...";

    const loadingMessage = addMessage(
        "assistant",
        "Searching the financial knowledge base and preparing an answer..."
    );

    try {
        const response = await fetch(`${API_BASE}/api/ask`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                question: question
            })
        });

        if (!response.ok) {
            throw new Error(`Request failed with status ${response.status}`);
        }

        const result = await response.json();

        loadingMessage.querySelector("p").textContent =
            result.answer || "No answer was returned.";

        addSources(loadingMessage, result.sources);

    } catch (error) {
        console.error("Assistant error:", error);

        loadingMessage.querySelector("p").textContent =
            "Sorry, I could not retrieve an answer. Please check that the API is running and try again.";

    } finally {
        submitButton.disabled = false;
        submitButton.textContent = "Ask SpendSense";
        questionInput.focus();
    }
});
