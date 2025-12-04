# models/res_config_settings.py
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import requests
import logging

_logger = logging.getLogger(__name__)


class LlmAssistantModel(models.Model):
    _name = "llm.assistant.model"
    _description = "LLM Assistant Model"

    name = fields.Char("Name", required=True)        # Anzeige im Dropdown
    model_id = fields.Char("Model ID", required=True, index=True)
    owned_by = fields.Char("Owned By")

    _sql_constraints = [
        ("model_id_unique", "unique(model_id)", "Model ID must be unique."),
    ]


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
    llm_model_id = fields.Many2one(
        "llm.assistant.model",
        string="Model",
        help="Wähle hier das zu verwendende LLM-Modell.",
    )
    llm_available_models = fields.Text(
        string="Available Models",
        help="Nur temporär – wird später entfernt.",
    )

    def set_values(self):
        super().set_values()
        self.ensure_one()
        icp = self.env["ir.config_parameter"].sudo()
        icp.set_param("llm_assistant.base_url", self.llm_base_url or "")
        icp.set_param("llm_assistant.api_key", self.llm_api_key or "")
        icp.set_param(
            "llm_assistant.model_id",
            self.llm_model_id.model_id if self.llm_model_id else "",
        )

    @api.model
    def get_values(self):
        res = super().get_values()
        icp = self.env["ir.config_parameter"].sudo()
        base_url = icp.get_param(
            "llm_assistant.base_url", "https://maas.ai-2.kvant.cloud"
        )
        api_key = icp.get_param("llm_assistant.api_key", "")
        model_id_str = icp.get_param("llm_assistant.model_id", "")

        model_rec = False
        if model_id_str:
            model_rec = (
                self.env["llm.assistant.model"]
                .search([("model_id", "=", model_id_str)], limit=1)
            )

        res.update(
            llm_base_url=base_url,
            llm_api_key=api_key,
            llm_model_id=model_rec.id if model_rec else False,
        )
        return res

    def action_fetch_llm_models(self):
        """Button: ruft /models auf und aktualisiert die Dropdown-Liste."""
        self.ensure_one()
        icp = self.env["ir.config_parameter"].sudo()

        base_url = self.llm_base_url or icp.get_param("llm_assistant.base_url", "")
        api_key = self.llm_api_key or icp.get_param("llm_assistant.api_key", "")

        if not base_url or not api_key:
            raise UserError(
                _("Bitte zuerst LLM Base URL und LLM API Key konfigurieren.")
            )

        url = base_url.rstrip("/") + "/models"
        headers = {
            "accept": "application/json",
            "x-litellm-api-key": api_key,
        }
        params = {
            "return_wildcard_routes": "false",
            "include_model_access_groups": "false",
            "only_model_access_groups": "false",
            "include_metadata": "false",
        }

        try:
            resp = requests.get(url, headers=headers, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            _logger.exception("Fehler beim Laden der LLM-Modelle")
            raise UserError(_("Fehler beim Laden der Modelle: %s") % e)

        if isinstance(data, dict) and "data" in data:
            iterable = data["data"]
        else:
            iterable = data

        Model = self.env["llm.assistant.model"]

        # MVP: alte Liste leeren
        Model.search([]).unlink()

        for m in iterable or []:
            mid = m.get("id")
            owned_by = m.get("owned_by")
            if not mid:
                continue
            Model.create(
                {
                    "name": mid,         # was im Dropdown angezeigt wird
                    "model_id": mid,
                    "owned_by": owned_by,
                }
            )

        # Formular neu laden, damit das Dropdown die neue Liste kennt
        return {
            "type": "ir.actions.client",
            "tag": "reload",
        }
