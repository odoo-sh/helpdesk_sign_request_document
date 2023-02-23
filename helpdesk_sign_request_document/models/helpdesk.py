# copyright 2023 Sodexis
# license OPL-1 (see license file for full copyright and licensing details).


from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    sign_request_ids = fields.Many2many(
        "sign.request",
        string="Requested Signatures"
    )
    sign_request_count = fields.Integer(compute="_compute_sign_request_count")

    @api.depends("sign_request_ids")
    def _compute_sign_request_count(self):
        for ticket in self:
            ticket.sign_request_count = len(ticket.sign_request_ids)

    def unlink(self):
        if self.sign_request_ids.filtered(lambda s: s.state != "canceled"):
            raise ValidationError(
                _(
                    '''"You can't delete a contract linked to a signed document,
                        archive it instead."'''
                )
            )
        return super().unlink()

    def open_helpdesk_sign_requests(self):
        self.ensure_one()
        if len(self.sign_request_ids.ids) == 1:
            return self.sign_request_ids.go_to_document()

        return {
            "type": "ir.actions.act_window",
            "name": "Signature Requests",
            "view_mode": "kanban",
            "res_model": "sign.request",
            "domain": [("id", "in", self.sign_request_ids.ids)],
        }
