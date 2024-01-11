# -*- coding: utf-8 -*-

from odoo import fields, api, models, _
from odoo.exceptions import AccessError, UserError, ValidationError
from dateutil.relativedelta import relativedelta
from odoo.tools.safe_eval import safe_eval


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # contract_id = fields.Many2one('contract.cadre', string=_("Contrat Cadre"),
    #                               domain="['|',('customer_id', '=', partner_id),('secondary_customer_ids', 'in', partner_id)]")

    subscription_ids = fields.One2many('sale.order', 'sale_id', string=_("Subscriptions"))
    subscription_count = fields.Integer(compute="_get_counts", string=_("Nombre des Subscriptions"))
    carnet_ids = fields.One2many('project.carnet', 'sale_id', string=_("Carnets"))
    carnet_count = fields.Integer(compute="_get_counts", string=_("Nombre des Carnets"))
    object = fields.Char(copy=False, required=0)

    def _get_counts(self):
        for r in self:
            r.subscription_count = len(r.subscription_ids) if r.subscription_ids else 0
            r.carnet_count = len(r.carnet_ids) if r.carnet_ids else 0

    def action_open_subscriptions(self):
        super(SaleOrder, self).action_open_subscriptions()
        return {
            "name": _("Subscriptions"),
            "type": "ir.actions.act_window",
            "res_model": "sale.order",
            "view_mode": "tree,form",
            "domain": [("id", "in", self.subscription_ids.ids)],
            "context": {"default_sale_id": self.id},
        }

    def get_carnet(self):
        return {
            "name": _("Carnets"),
            "type": "ir.actions.act_window",
            "res_model": "project.carnet",
            "view_mode": "tree,form",
            "domain": [("id", "in", self.carnet_ids.ids)],
            "context": {"default_sale_id": self.id},
        }

    def action_view_task(self):
        self.ensure_one()

        list_view_id = self.env.ref('project.view_task_tree2').id
        form_view_id = self.env.ref('project.view_task_form2').id

        action = {'type': 'ir.actions.act_window_close'}
        task_projects = self.tasks_ids.mapped('project_id')
        if len(task_projects) == 1 and len(
                self.tasks_ids) > 1:  # redirect to task of the project (with kanban stage, ...)
            action = self.with_context(active_id=task_projects.id).env['ir.actions.actions']._for_xml_id(
                'project.act_project_project_2_project_task_all')
            action['domain'] = [('id', 'in', self.tasks_ids.ids)]
            if action.get('context'):
                eval_context = self.env['ir.actions.actions']._get_eval_context()
                eval_context.update({'active_id': task_projects.id})
                action_context = safe_eval(action['context'], eval_context)
                action_context.update(eval_context)
                action['context'] = action_context
        else:
            action = self.env["ir.actions.actions"]._for_xml_id("project.action_view_task")
            action['domain'] = [('id', 'in', self.tasks_ids.ids)]
            action['context'] = {}  # erase default context to avoid default filter
            if len(self.tasks_ids) > 1:  # cross project kanban task
                action['views'] = [[False, 'kanban'], [list_view_id, 'tree'], [form_view_id, 'form'], [False, 'graph'],
                                   [False, 'calendar'], [False, 'pivot']]
            elif len(self.tasks_ids) == 1:  # single task -> form view
                action['views'] = [(form_view_id, 'form')]
                action['res_id'] = self.tasks_ids.id
        # filter on the task of the current SO
        action.setdefault('context', {})
        action['context'] = {'default_sale_order_id': self.id, 'default_contract_id': self.contract_id.id}
        # action['context'].update(
        #     {'search_default_sale_order_id': self.id})
        return action

    @api.onchange('partner_id')
    def _resent_contract(self):
        if self.partner_id:
            contract = self.env['contract.cadre'].search(
                ['|', ('customer_id', '=', self.partner_id.id), ('secondary_customer_ids', 'in', self.partner_id.id)])
            contr_dict = {}
            if contract:
                for sec in contract:
                    if sec.first_date in contr_dict.keys():
                        contr_dict[sec.first_date] |= sec
                    else:
                        contr_dict[sec.first_date] = sec
                first_contract = [x for x in sorted(contr_dict.keys())]
                self.contract_id = contr_dict[first_contract[-1]][0]
            else:
                self.contract_id = False
        else:
            self.contract_id = False

    def action_confirm(self):
        if not self.contract_id:
            raise ValidationError(_('Please fill the contract cadre before confirming the order'))
        else:
            return super(SaleOrder, self).action_confirm()

    #     for r in self:
    #         if r.contract_id:
    #             list_product = []
    #             sufixe = self.env['ir.sequence'].next_by_code('project.carnet.suffixe') or ''
    #             for rec in r.order_line:
    #                 # if not r.recurrence_id:
    #                 if rec.product_template_id and not rec.product_template_id.type_1 and rec.display_type in (
    #                         'line_note', 'line_section'):
    #                     list_product.append(rec.product_template_id)
    #                 elif rec.product_template_id.type_1 == 'carnet':
    #                         self.env['project.carnet'].create({
    #                             'name': rec.product_template_id.name + "/" + rec.order_id.partner_id.name + "/" +  str(sufixe) ,
    #                             'partner_id': self.partner_id.id,
    #                             'contract_id': self.contract_id.id,
    #                             'sale_id': self.id,
    #                             'sale_line_id': rec.id,
    #                             'project_id': self.company_id.carnet_id.id,
    #                             'first_date': self.date_order,
    #                             'last_date': self.date_order + relativedelta(years=1),
    #                             'capacity': rec.product_uom_qty,
    #                             'default_code': rec.product_template_id.default_code,
    #                             'desc': rec.name,
    #                         })
    #
    #             if not list_product:
    #                 super(SaleOrder, self).action_confirm()
    #             else:
    #                 mess = ""
    #                 for l in list_product:
    #                     mess += "%s," % l.name
    #                 message_id = self.env['sale.message.wizard'].create(
    #                     {
    #                         'message': "Les articles %s n'ont pas de type, vous pouvez pas confirmer cette commande !" % mess})
    #                 return {
    #                     'name': 'Message',
    #                     'type': 'ir.actions.act_window',
    #                     'view_mode': 'form',
    #                     'res_model': 'sale.message.wizard',
    #                     'res_id': message_id.id,
    #                     'target': 'new',
    #                     'context': {'default_sale_id': r.id},
    #                 }
    #         else:
    #             raise ValidationError(_("Please fill in the framework contract!"))

    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals['contract_id'] = self.contract_id.id
        return invoice_vals


class SaleMessageWizard(models.TransientModel):
    _name = 'sale.message.wizard'
    _description = "Message Popup"
    message = fields.Text('Message', required=True)
    sale_id = fields.Many2one('sale.order', store=1)

    def action_close(self):
        return {'type': 'ir.actions.act_window_close'}
