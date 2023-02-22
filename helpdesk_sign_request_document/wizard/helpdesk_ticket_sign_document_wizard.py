# Copyright 2023 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HelpdeskSignDocumentWizard(models.TransientModel):
    _name = "helpdesk.ticket.sign.document.wizard"
    _description = "Sign document in Helpdesk"

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        if (
            "partner_id" in fields_list
            and not defaults.get("partner_id")
            and defaults.get("ticket_id")
        ):
            ticket = self.env["helpdesk.ticket"].browse(defaults.get("ticket_id"))
            if not ticket.partner_id.is_company and ticket.partner_id.email:
                defaults["partner_id"] = ticket.partner_id.id
        return defaults

    ticket_id = fields.Many2one(
        "helpdesk.ticket",
        string="ticket",
        default=lambda self: self.env.context.get("active_id"),
    )
    employee_id = fields.Many2one("hr.employee", string="Employee", required="1")
    partner_id = fields.Many2one(
        "res.partner",
        required="1",
        string="Customer",
        domain="[('is_company','=',False),('email','!=',False)]",
    )

    sign_template_id = fields.Many2one(
        "sign.template",
        string="Document to Sign",
        required=True,
        domain="[('tag_ids','ilike','customer service')]",
        help="Document that the employee will have to sign.",
    )

    subject = fields.Char(required=True, default="Signature Request")
    message = fields.Html()

    def validate_helpdesk_signature(self):
        if not self.employee_id.user_id and not self.employee_id.user_id.partner_id:
            raise ValidationError(_("Employee must be linked to a user and a partner."))

        sign_request = self.env["sign.request"]
        if not self.check_access_rights("create", raise_exception=False):
            sign_request = sign_request.sudo()

        res = sign_request.initialize_new(
            self.sign_template_id.id,
            [
                {
                    "role": self.env["ir.model.data"].xmlid_to_res_id(
                        "sign.sign_item_role_employee"
                    ),
                    "partner_id": self.employee_id.user_id.partner_id.id,
                },
                {
                    "role": self.env["ir.model.data"].xmlid_to_res_id(
                        "sign.sign_item_role_customer"
                    ),
                    "partner_id": self.partner_id.id,
                },
            ],
            [],
            "Signature Request -" + self.ticket_id.name,
            self.subject,
            self.message,
        )

        sign_request = self.env["sign.request"].browse(res["id"])
        if not self.check_access_rights("write", raise_exception=False):
            sign_request = sign_request.sudo()

        sign_request.toggle_favorited()
        sign_request.action_sent()
        sign_request.write({"state": "sent"})
        sign_request.request_item_ids.write({"state": "sent"})

        self.ticket_id.sign_request_ids += sign_request

        self.ticket_id.message_post(
            body=_(
                "%(user)s requested a new signature on document: %(template)s."
                "<br/>%(employee)s and %(partner)s are the signatories.",
                user=self.env.user.display_name,
                template=self.sign_template_id.name,
                employee=self.employee_id.display_name,
                partner=self.partner_id.display_name,
            )
        )

        if self.env.user.id == self.employee_id.user_id.id:
            return sign_request.go_to_document()
