/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

class LlmChatWidget extends Component {
    setup() {
        this.rpc = useService("rpc");
        this.state = useState({
            open: false,
            messages: [],
            input: "",
            lastRawRequest: null,
            lastRawResponse: null,
        });
    }

    toggle() {
        this.state.open = !this.state.open;
    }

    async sendMessage(ev) {
        ev.preventDefault();
        const text = this.state.input.trim();
        if (!text) {
            return;
        }
        this.state.messages.push({ from: "user", text });
        this.state.input = "";

        const context = {}; // MVP: leer, später Modell/ResId reingeben

        const resp = await this.rpc("/llm/chat", { message: text, context });

        this.state.messages.push({ from: "bot", text: resp.reply || "(keine Antwort)" });

        // Debug: hier in String serialisieren, damit das Template nur t-esc machen muss
        this.state.lastRawRequest = resp.raw_request
            ? JSON.stringify(resp.raw_request, null, 2)
            : null;
        this.state.lastRawResponse = resp.raw_response
            ? JSON.stringify(resp.raw_response, null, 2)
            : null;
    }
}

LlmChatWidget.template = "odoo_llm_assistant.LlmChatWidget";

registry.category("systray").add("llm_chat_widget", {
    Component: LlmChatWidget,
    props: {},
});
