from odoo import api, fields, models


class ChatgptPricing(models.Model):
    _name = 'chatgpt.pricing'
    _description = 'chatgpt.pricing'

    model = fields.Char(string="Model")
    price = fields.Float(string="Price", digits=(2, 4))
    tokens = fields.Integer(string="Tokens")
    currency_id = fields.Many2one('res.currency', string="Currency")

    @api.depends(
        'line_ids',
        'line_ids.total_tokens',
    )
    def _compute_total_tokens(self):
        for record in self:
            record.total_tokens = sum(record.line_ids.mapped('total_tokens'))
