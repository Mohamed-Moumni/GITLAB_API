# -*- coding: utf-8 -*-
from odoo import api, models
from odoo.http import request


class IrUiMenu(models.Model):
    _name = 'ir.ui.menu'
    _description = 'Menu'
    _inherit = 'ir.ui.menu'

    @api.model
    def load_menus(self, debug):
        menus = super(IrUiMenu, self).load_menus(debug)
        cids = request and request.httprequest.cookies.get('cids')
        if cids:
            cids = [int(cid) for cid in cids.split(',')]
        company = self.env['res.company'].browse(cids[0]) \
            if cids and all([cid in self.env.user.company_ids.ids for cid in cids]) \
            else self.env.user.company_id
        menus['root']['backgroundImage'] = bool(company.background_image)
        return menus
