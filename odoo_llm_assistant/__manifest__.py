# __manifest__.py
{
    "name": "LLM Assistant Chat",
    "version": "1.0",
    "category": "Tools",
    "summary": "Globaler Chat-Assistent mit LLM-Anbindung",
    "depends": ["web"],
    "data": [
        "views/res_config_settings_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "odoo_llm_assistant/static/src/js/llm_chat_widget.js",
        ],
    },
    "installable": True,
    "application": False,
}
