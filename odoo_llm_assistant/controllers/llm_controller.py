from odoo import http
from odoo.http import request
import requests

class LlmChatController(http.Controller):

    @http.route('/llm/chat', type='json', auth='user', methods=['POST'], csrf=False)
    def llm_chat(self, message, context=None):
        """Phase 1: direkter Call an das LLM (KVANT / LiteLLM-kompatibel)."""
        user = request.env.user
        icp = request.env["ir.config_parameter"].sudo()

        base_url = icp.get_param("llm_assistant.base_url", "https://maas.ai-2.kvant.cloud").rstrip("/")
        api_key = icp.get_param("llm_assistant.api_key")
        model_id = icp.get_param("llm_assistant.model_id", "test-llama4-maverick")

        if not api_key:
            return {"error": "LLM API Key ist nicht konfiguriert.", "reply": "Kein API-Key konfiguriert."}

        # Ziel-Endpoint – anpassen falls anders
        url = base_url + "/chat/completions"

        system_prompt = "Du bist ein hilfreicher Assistent, der Odoo-Anwender unterstützt."
        user_prompt = message

        payload = {
            "model": model_id,
            "messages": [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
        }

        headers = {
            "Content-Type": "application/json",
            "x-litellm-api-key": api_key,
            "accept": "application/json",
        }

        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=60)
            resp.raise_for_status()
            data = resp.json()

            # OpenAI-kompatibel: choices[0].message.content
            reply = data.get("choices", [{}])[0].get("message", {}).get("content", "")

            return {
                "reply": reply or "(keine Antwort vom Modell)",
                "raw_request": payload,
                "raw_response": data,
            }
        except Exception as e:
            return {
                "reply": f"Fehler beim Aufruf des LLM: {e}",
                "error": str(e),
            }
