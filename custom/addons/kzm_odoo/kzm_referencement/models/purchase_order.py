
from odoo import models, _
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def button_confirm(self):
        for rec in self:
            res = super(PurchaseOrder, self).button_confirm()
            if not rec.partner_id.referenced:
                raise ValidationError(_("Le fournisseur n'est pas référencé!"))
            if len(rec.order_line.filtered(lambda r: not r.product_id.referenced and r.display_type == False)) > 0:
                products = '\n- '.join(
                    rec.order_line.filtered(lambda r: not r.product_id.referenced).mapped('product_id.name'))
                msg = f"Les articles suivants ne sont pas référencés : \n - {products}"
                raise ValidationError(msg)
            else:
                return res
