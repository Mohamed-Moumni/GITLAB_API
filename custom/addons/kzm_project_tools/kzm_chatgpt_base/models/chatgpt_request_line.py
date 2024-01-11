from odoo import api, fields, models


class ChatgptRequestLine(models.Model):
    _name = 'chatgpt.request.line'
    _description = 'chatgpt.request.line'
    _rec_name = 'request_uuid'

    request_id = fields.Many2one('chatgpt.request', string="Request")
    partner_id = fields.Many2one('res.partner', string="Client")

    response_json = fields.Text(string="Response JSON")
    request_uuid = fields.Char(string="Request UUID")
    model = fields.Char(string="Model")
    input_message = fields.Text(string="Input message")
    posted_response = fields.Text(string="Posted response")
    total_tokens = fields.Integer(string="Total tokens")
    amount = fields.Float(string="Amount", compute="_compute_amount", digits=(2, 6))

    @api.depends('model', 'total_tokens')
    def _compute_amount(self):
        for record in self:
            domain = [('model', '=', record.model)]
            pricing_id = self.env['chatgpt.pricing'].search(domain, limit=1)
            record.amount = pricing_id.price / pricing_id.tokens * record.total_tokens if pricing_id else 0

    def _check_request_id(self):
        for record in self:
            if not record.request_id:
                domain = [('partner_id', '=', record.partner_id.id)]
                request_id = self.env['chatgpt.request'].search(domain, limit=1)
                if not request_id:
                    request_id = self.env['chatgpt.request'].create({'partner_id': record.partner_id.id})
                record.request_id = request_id

    @api.model
    def create(self, vals):
        res = super().create(vals)
        res._check_request_id()
        return res
