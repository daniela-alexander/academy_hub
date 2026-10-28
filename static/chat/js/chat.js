(function () {
    const root = document.getElementById("chat-root");
    if (!root) return;

    const conversationId = root.dataset.conversationId;
    const protocol = window.location.protocol === "https:" ? "wss" : "ws";
    const wsUrl = `${protocol}://${window.location.host}/ws/chat/${conversationId}/`;

    const ws = new WebSocket(wsUrl);
    const list = document.getElementById("messages-list");
    const form = document.getElementById("message-form");
    const input = document.getElementById("message-text");

    ws.onopen = function () {
        console.log("WebSocket conectado");
    };

    ws.onmessage = function (event) {
        const data = JSON.parse(event.data);
        if (data.type !== "message") return;

        const article = document.createElement("article");
        const header = document.createElement("p");
        const sender = document.createElement("strong");
        sender.textContent = data.sender;
        header.appendChild(sender);
        header.appendChild(document.createTextNode(" — " + data.created_at));

        const body = document.createElement("p");
        body.textContent = data.text;

        article.appendChild(header);
        article.appendChild(body);
        list.appendChild(article);
        list.appendChild(document.createElement("hr"));

        list.scrollTop = list.scrollHeight;
    };

    form.addEventListener("submit", function (event) {
        event.preventDefault();
        const text = input.value.trim();
        if (!text) return;

        if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ text: text }));
            input.value = "";
        } else {
            // Fallback a POST si el socket no está abierto
            form.submit();
        }
    });
})();
