from odoo import models, api


class Module(models.Model):
    _inherit = "ir.module.module"

    @api.multi
    def _button_immediate_function(self, function):
        with api.Environment.manage():
            function(self)
        env = api.Environment(self._cr, self._uid, self._context)
        config = env['res.config'].next() or {}
        if config.get('type') != 'ir.actions.act_window_close':
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }

        # reload the client; open the first available root menu
        menu = env['ir.ui.menu'].search([('parent_id', '=', False)])[:1]
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
            'params': {'menu_id': menu.id},
        }
