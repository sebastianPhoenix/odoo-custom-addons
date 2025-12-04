from odoo import api, fields, models
import requests

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    llm_base_url = fields.Char(
        string="LLM Base URL",
        default="https://maas.ai-2.kvant.cloud",
        help="Basis-URL des KVANT LLM-Clusters",
    )
    llm_api_key = fields.Char(
        string="LLM API Key",
        help="x-litellm-api-key für KVANT",
    )
    llm_model_id = fields.Char(
        string="Model ID",
        help="z.B. test-llama4-maverick",
    )

    # optional: nur zum Anzeigen, nicht gespeichert
    llm_available_models = fields.Text(
        string="Verfügbare Modelle (Nur Anzeige)",
        readonly=True,
    )

    def set_values(self):
        super().set_values()
        icp = self.env["ir.config_parameter"].sudo()
        self.ensure_one()
        icp.set_param("llm_assistant.base_url", self.llm_base_url or "")
        icp.set_param("llm_assistant.api_key", self.llm_api_key or "")
        icp.set_param("llm_assistant.model_id", self.llm_model_id or "")

    @api.model
    def get_values(self):
        res = super().get_values()
        icp = self.env["ir.config_parameter"].sudo()
        res.update(
            llm_base_url=icp.get_param("llm_assistant.base_url", "https://maas.ai-2.kvant.cloud"),
            llm_api_key=icp.get_param("llm_assistant.api_key", ""),
            llm_model_id=icp.get_param("llm_assistant.model_id", ""),
        )
        return res

    def action_fetch_llm_models(self):
        """Button in den Settings: ruft GET /models auf und zeigt das Ergebnis im Textfeld."""
        self.ensure_one()
        icp = self.env["ir.config_parameter"].sudo()
        base_url = self.llm_base_url or icp.get_param("llm_assistant.base_url", "")
        api_key = self.llm_api_key or icp.get_param("llm_assistant.api_key", "")

        if not base_url or not api_key:
            self.llm_available_models = "Bitte Base URL und API Key speichern."
            return

        url = base_url.rstrip("/") + "/models"
        headers = {
            "accept": "application/json",
            "x-litellm-api-key": api_key,
        }
        try:
            resp = requests.get(
                url,
                headers=headers,
                params={
                    "return_wildcard_routes": "false",
                    "include_model_access_groups": "false",
                    "only_model_access_groups": "false",
                    "include_metadata": "false",
                },
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()

            # Erwartetes Format: {"data": [ { "id": "...", ... }, ... ] } oder direkt Liste
            models_list = []
            if isinstance(data, dict) and "data" in data:
                iterable = data["data"]
            else:
                iterable = data

            for m in iterable:
                mid = m.get("id")
                owned_by = m.get("owned_by")
                models_list.append(f"- {mid} (owned_by={owned_by})")

            self.llm_available_models = "\n".join(models_list) or "Keine Modelle gefunden."
        except Exception as e:
            self.llm_available_models = f"Fehler beim Laden der Modelle: {e}"
