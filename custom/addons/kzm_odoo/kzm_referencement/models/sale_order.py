from odoo import models, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        for rec in self:
            res = super(SaleOrder, self).action_confirm()
            if not rec.partner_id.referenced:
                raise ValidationError(_("Le client n'est pas référencé!"))
            if len(rec.order_line.filtered(lambda r: not r.product_id.referenced and r.display_type == False)) > 0:
                products = '\n- '.join(
                    rec.order_line.filtered(lambda r: not r.product_id.referenced).mapped('product_id.name'))
                msg = f"Les articles suivants ne sont pas référencés : \n - {products}"
                raise ValidationError(msg)
            else:
                return res
