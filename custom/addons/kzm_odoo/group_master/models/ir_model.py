# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models


class IrModel(models.Model):
    _inherit = "ir.model"

    def list_models(self):
        return [
            'product.category',
            'product.attribute',
            'uom.categ',
            'uom.uom',
            'product.template',
            'product.supplierinfo',
            'product.pricelist',
            'product.pricelist.item',
            'product.product',
            'res.country',
            'res.country.state',
            'res.partner',
            'res.partner.bank',
            'res.partner.category',
            'res.partner.title',
            'res.bank',
            # 'hr.department',
        ]

    def create_groups(self):
        id1 = self.env.ref('group_master.group_master_product', raise_if_not_found=False)
        if not id1:
            id1 = self.env['res.groups'].create({
                'name': "Administrateur des articles",
                'category_id': self.env.ref('base.module_category_hidden').id,
                'users': [(6, 0, [2])]
            })
            self.env['ir.model.data'].create({
                'module': 'group_master',
                'name': 'group_master_product',
                'noupdate': True,
                'model': 'res.groups',
                'res_id': id1.id
            })
        id2 = self.env.ref('group_master.group_master_partner', raise_if_not_found=False)
        if not id2:
            id2 = self.env['res.groups'].create({
                'name': "Administrateur des clients/Fournisseurs",
                'category_id': self.env.ref('base.module_category_hidden').id,
                'users': [(6, 0, [2])]
            })
            self.env['ir.model.data'].create({
                'module': 'group_master',
                'name': 'group_master_partner',
                'noupdate': True,
                'model': 'res.groups',
                'res_id': id2.id
            })
        return [id1.id, id2.id]

    def init(self):
        cr = self._cr
        # id3 = self.env.ref('group_master.group_master_department', raise_if_not_found=False)

        query = """
                        update ir_model_access
                        set  perm_read = True, perm_write =    False, perm_unlink = False, perm_create = False
                        where
                        group_id not in (select id from res_groups where id in %s)
                        and model_id in (select id from ir_model where model in %s)
                    """
        cr.execute(query, (tuple(self.create_groups()), tuple(self.list_models())))

# ir_model()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
