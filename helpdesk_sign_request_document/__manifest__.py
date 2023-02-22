# Copyright 2023 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).

{
    "name": "Helpdesk Sign Request Document",
    "summary": """
        Short (1 phrase/line) summary of the module"s purpose, used as
        subtitle on modules listing or apps.openerp.com""",
    "version": "14.0.1.0.0",
    "category": "Uncategorized",
    "website": "https://sodexis.com/",
    "author": "Sodexis",
    "license": "OPL-1",
    "installable": True,
    "application": False,
    "depends": ["helpdesk", "sign"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/helpdesk_ticket_sign_document_wizard.xml",
        "views/helpdesk_views.xml",
    ],
}
