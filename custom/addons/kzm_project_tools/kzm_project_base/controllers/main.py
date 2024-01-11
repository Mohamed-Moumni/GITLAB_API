from odoo import http
from odoo.http import request
import base64
import logging
from odoo.tools.translate import _
from odoo.addons.helpdesk.controllers.portal import portal_pager, CustomerPortal
from odoo.osv.expression import OR, AND
from odoo.tools import groupby as groupbyelem
from odoo.http import request
from odoo.addons.portal.controllers.portal import pager as portal_pager
from odoo.addons.web.controllers.main import Home

from operator import itemgetter
from markupsafe import Markup

_logger = logging.getLogger(__name__)


class MyController(http.Controller):

    @http.route(['/dashboard'], auth='user', website=True)
    def handler(self):
        user = request.env.user
        company = request.env.company
        partner_id = user.partner_id

        contract_id = request.env['contract.cadre'].sudo().search(
            ['|', '|', ('customer_id', '=', user.partner_id.id), ('secondary_customer_ids', 'in', user.partner_id.id),
             ('contact_ids', 'in', user.partner_id.id)], limit=1)
        if contract_id:
            tickets = request.env['helpdesk.ticket'].sudo().search(
                ['|', ('contract_id', '=', contract_id.id), ('partner_id', '=', user.partner_id.id)], limit=5,
                order='create_date desc')
        else:
            tickets = request.env['helpdesk.ticket'].sudo().search([('partner_id', '=', user.partner_id.id)], limit=5,
                                                                   order='id desc')
        # tickets = sorted(tickets, key=lambda t: t.id)
        valid = -1

        values = {
            'tickets': tickets,
            'company': company,
            'contract': contract_id,
            'partner': partner_id,
            'valid': valid
        }
        return request.render("kzm_project_base.dashboard_template", values)

    @http.route(['/openticket'], type='http', auth='user', website=True)
    def open_ticket(self):

        values = {
        }

        return request.render("kzm_project_base.openticket_form", values)

    @http.route(['/my/invoices'], type='http', auth='user', website=True)
    def my_invoices(self):
        user = request.env.user

        contract_id = request.env['contract.cadre'].sudo().search(
            ['|', '|', ('customer_id', '=', user.partner_id.id), ('secondary_customer_ids', 'in', user.partner_id.id),
             ('contact_ids', 'in', user.partner_id.id)], limit=1)

        invoices = contract_id.move_ids

        values = {
            'invoices': invoices
        }

        return request.render("kzm_project_base.myinvoices", values)

    @http.route(['/my/orders'], type='http', auth='user', website=True)
    def my_orders(self):
        user = request.env.user

        contract_id = request.env['contract.cadre'].sudo().search(
            ['|', '|', ('customer_id', '=', user.partner_id.id), ('secondary_customer_ids', 'in', user.partner_id.id),
             ('contact_ids', 'in', user.partner_id.id)], limit=1)

        orders = contract_id.order_ids.filtered(lambda o: o.move_type != 'entry')

        values = {
            'orders': orders
        }

        return request.render("kzm_project_base.myorders", values)

    @http.route(['/timesheet'], type='http', auth='user', website=True)
    def my_timesheets(self):
        user = request.env.user

        contract_id = request.env['contract.cadre'].sudo().search(
            ['|', '|', ('customer_id', '=', user.partner_id.id), ('secondary_customer_ids', 'in', user.partner_id.id),
             ('contact_ids', 'in', user.partner_id.id)], limit=1)

        timesheet_ids = contract_id.timesheet_ids

        values = {
            'timesheet_ids': timesheet_ids
        }

        return request.render("kzm_project_base.timesheet", values)

    @http.route(['/tasks'], type='http', auth='user', website=True)
    def my_tasks(self):
        user = request.env.user

        contract_id = request.env['contract.cadre'].sudo().search(
            ['|', '|', ('customer_id', '=', user.partner_id.id), ('secondary_customer_ids', 'in', user.partner_id.id),
             ('contact_ids', 'in', user.partner_id.id)], limit=1)

        task_ids = contract_id.task_ids
        print(contract_id)
        print(contract_id.task_ids)

        values = {
            'task_ids': task_ids
        }

        return request.render("kzm_project_base.tasks", values)

    @http.route(['/subscription'], type='http', auth='user', website=True)
    def my_subsctription(self):
        user = request.env.user

        contract_id = request.env['contract.cadre'].sudo().search(
            ['|', '|', ('customer_id', '=', user.partner_id.id), ('secondary_customer_ids', 'in', user.partner_id.id),
             ('contact_ids', 'in', user.partner_id.id)], limit=1)

        subscription_ids = contract_id.subscription_ids

        values = {
            'subscription_ids': subscription_ids
        }

        return request.render("kzm_project_base.subscriptions", values)

    @http.route(['/carnets'], type='http', auth='user', website=True)
    def carnets(self):
        user = request.env.user

        contract_id = request.env['contract.cadre'].sudo().search(
            ['|', '|', ('customer_id', '=', user.partner_id.id), ('secondary_customer_ids', 'in', user.partner_id.id),
             ('contact_ids', 'in', user.partner_id.id)], limit=1)

        carnet_ids = contract_id.carnet_ids

        values = {
            'carnet_ids': carnet_ids,
            'page_name': 'carnets'
        }

        return request.render("kzm_project_base.carnets", values)

    @http.route(['/openticket/submit'],
                type='http', auth="public", website=True, methods=["POST"])
    def open_ticket_form_submit(self, sujet, description, pj, **kwargs):

        user = request.env.user

        contract_id = request.env['contract.cadre'].sudo().search(
            ['|', '|', ('customer_id', '=', user.partner_id.id), ('secondary_customer_ids', 'in', user.partner_id.id),
             ('contact_ids', 'in', user.partner_id.id)])
        url = '/dashboard'
        valid = -1

        if contract_id:
            ticket_id = request.env['helpdesk.ticket'].sudo().create({
                'name': sujet,
                'partner_id': user.partner_id.id,
                'description': description,
                'contract_id': contract_id.id
            })

            if 'pj' in request.params:
                attached_files = request.httprequest.files.getlist('pj')
                for attachment in attached_files:
                    attached_file = attachment.read()
                    request.env['ir.attachment'].sudo().create({
                        'name': attachment.filename,
                        'res_model': 'helpdesk.ticket',
                        'res_id': ticket_id.id,
                        'type': 'binary',
                        # 'datas_fname': attachment.filename,
                        'datas': base64.b64encode(attached_file),
                    })
            url = "/helpdesk/ticket/%s" % ticket_id.id
            _logger.info("New ticket created by %s" % (request.env.uid))
            valid = 1
            values = {
                'valid': valid,
                'ticket_id': ticket_id.id

            }
            return request.render("kzm_project_base.openticket_form", values)
        else:
            valid = 0
            values = {
                'valid': valid
            }
            return request.render("kzm_project_base.openticket_form", values)

    @http.route(['/', '/my', '/my/home'], auth='user', website=True)
    def redirect_to_dashboard(self):
        values = {}

        return request.redirect('/dashboard')

    @http.route(['/my/tasks'], auth='user', website=True)
    def redirect_to_my_tasks(self):
        values = {}

        return request.redirect('/tasks')

    @http.route(['/my/subscription'], auth='user', website=True)
    def redirect_to_my_subscription(self):
        values = {}

        return request.redirect('/subscription')

    @http.route(['/my/invoices'], auth='user', website=True)
    def redirect_to_my_invoces(self):
        values = {}

        return request.redirect('/my/invoices')

    @http.route([
        "/carnet/<int:carnet_id>",

    ], type='http', auth='user', website=True)
    def carnets_followup(self, carnet_id=None, access_token=None, **kw):

        carnet = request.env['project.carnet'].sudo().browse(carnet_id)

        values = {
            'carnet': carnet,
            'page_name': 'carnets'
        }

        return request.render("kzm_project_base.carnets_followup", values)

    # @http.route(['/helpdesk/ticket'],
    #             type='http', auth="public", website=True, methods=["POST"])
    # def cloture_ticket(self):
    #     if not self.state.is_clotured:
    #         cloture_stape = self.env['helpdesk.stage'].search([('is_clotured', '=', True)], limit=1)
    #         print("test ", cloture_stape)
    #         self.sudo().write({'state': cloture_stape.id})


class CustomerPortal(CustomerPortal):

    def _prepare_helpdesk_tickets_domain(self):

        user = request.env.user
        contract_id = request.env['contract.cadre'].sudo().search(
            ['|', '|', ('customer_id', '=', user.partner_id.id), ('secondary_customer_ids', 'in', user.partner_id.id),
             ('contact_ids', 'in', user.partner_id.id)], limit=1)
        if contract_id:
            return ['|', ('contract_id', '=', contract_id.id), ('partner_id', '=', user.partner_id.id)]
        else:
            return [('partner_id', '=', user.partner_id.id)]

    @http.route(['/my/tickets', '/my/tickets/page/<int:page>'], type='http', auth='user', website=True)
    def my_helpdesk_tickets(self, page=1, date_begin=None, date_end=None, sortby=None, filterby='all', search=None,
                            groupby='none', search_in='content', **kw):
        values = self._prepare_my_tickets_values(page, date_begin, date_end, sortby, filterby, search, groupby,
                                                 search_in)
        values.update({
            'show_real_charge_portal': request.env.company.show_real_charge_portal
        })

        return request.render("helpdesk.portal_helpdesk_ticket", values)

    @http.route([
        '/my/ticket/close/<int:ticket_id>',
        '/my/ticket/close/<int:ticket_id>/<access_token>',
    ], type='http', auth="public", website=True)
    def ticket_close(self, ticket_id=None, access_token=None, **kw):
        super().ticket_close(ticket_id, access_token, **kw)

    def _prepare_my_tickets_values(self, page=1, date_begin=None, date_end=None, sortby=None, filterby='all', search=None, groupby='none', search_in='content'):
        values = self._prepare_portal_layout_values()
        domain = self._prepare_helpdesk_tickets_domain()

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'reference': {'label': _('Reference'), 'order': 'id'},
            'name': {'label': _('Subject'), 'order': 'name'},
            'user': {'label': _('Assigned to'), 'order': 'user_id'},
            'stage': {'label': _('Stage'), 'order': 'stage_id'},
            'update': {'label': _('Last Stage Update'), 'order': 'date_last_stage_update desc'},
        }
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'assigned': {'label': _('Assigned'), 'domain': [('user_id', '!=', False)]},
            'unassigned': {'label': _('Unassigned'), 'domain': [('user_id', '=', False)]},
            'open': {'label': _('Open'), 'domain': [('close_date', '=', False)]},
            'closed': {'label': _('Closed'), 'domain': [('close_date', '!=', False)]},
        }
        searchbar_inputs = {
            'content': {'input': 'content', 'label': Markup(_('Search <span class="nolabel"> (in Content)</span>'))},
            'ticket_ref': {'input': 'ticket_ref', 'label': _('Search in Reference')},
            'message': {'input': 'message', 'label': _('Search in Messages')},
            'user': {'input': 'user', 'label': _('Search in Assigned to')},
            'status': {'input': 'status', 'label': _('Search in Stage')},
            'type': {'input': 'type', 'label': _('Search in Type')},
        }
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
            'stage': {'input': 'stage_id', 'label': _('Stage')},
            'user': {'input': 'user_id', 'label': _('Assigned to')},
            'type': {'input': 'ticket_type_id', 'label': _('Type')},
        }

        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        if filterby in ['last_message_sup', 'last_message_cust']:
            discussion_subtype_id = request.env.ref('mail.mt_comment').id
            messages = request.env['mail.message'].search_read([('model', '=', 'helpdesk.ticket'), ('subtype_id', '=', discussion_subtype_id)], fields=['res_id', 'author_id'], order='date desc')
            last_author_dict = {}
            for message in messages:
                if message['res_id'] not in last_author_dict:
                    last_author_dict[message['res_id']] = message['author_id'][0]

            ticket_author_list = request.env['helpdesk.ticket'].search_read(fields=['id', 'partner_id'])
            ticket_author_dict = dict([(ticket_author['id'], ticket_author['partner_id'][0] if ticket_author['partner_id'] else False) for ticket_author in ticket_author_list])

            last_message_cust = []
            last_message_sup = []
            ticket_ids = set(last_author_dict.keys()) & set(ticket_author_dict.keys())
            for ticket_id in ticket_ids:
                if last_author_dict[ticket_id] == ticket_author_dict[ticket_id]:
                    last_message_cust.append(ticket_id)
                else:
                    last_message_sup.append(ticket_id)

            if filterby == 'last_message_cust':
                domain = AND([domain, [('id', 'in', last_message_cust)]])
            else:
                domain = AND([domain, [('id', 'in', last_message_sup)]])

        else:
            domain = AND([domain, searchbar_filters[filterby]['domain']])

        if date_begin and date_end:
            domain = AND([domain, [('create_date', '>', date_begin), ('create_date', '<=', date_end)]])

        # search
        if search and search_in:
            search_domain = []
            if search_in == 'ticket_ref':
                search_domain = OR([search_domain, [('ticket_ref', 'ilike', search)]])
            if search_in == 'content':
                search_domain = OR([search_domain, ['|', ('name', 'ilike', search), ('description', 'ilike', search)]])
            if search_in == 'user':
                search_domain = OR([search_domain, [('user_id', 'ilike', search)]])
            if search_in == 'message':
                discussion_subtype_id = request.env.ref('mail.mt_comment').id
                search_domain = OR([search_domain, [('message_ids.body', 'ilike', search), ('message_ids.subtype_id', '=', discussion_subtype_id)]])
            if search_in == 'status':
                search_domain = OR([search_domain, [('stage_id', 'ilike', search)]])
            if search_in == 'type':
                search_domain = OR([search_domain, [('ticket_type_id', 'ilike', search)]])
            domain = AND([domain, search_domain])

        # pager
        tickets_count = request.env['helpdesk.ticket'].search_count(domain)
        pager = portal_pager(
            url="/my/tickets",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'search_in': search_in, 'search': search, 'groupby': groupby, 'filterby': filterby},
            total=tickets_count,
            page=page,
            step=self._items_per_page
        )

        tickets = request.env['helpdesk.ticket'].search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_tickets_history'] = tickets.ids[:100]

        if groupby != 'none':
            grouped_tickets = [request.env['helpdesk.ticket'].concat(*g) for k, g in groupbyelem(tickets, itemgetter(searchbar_groupby[groupby]['input']))]
        else:
            grouped_tickets = [tickets]

        values.update({
            'date': date_begin,
            'grouped_tickets': grouped_tickets,
            'page_name': 'ticket',
            'default_url': '/my/tickets',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_filters': searchbar_filters,
            'searchbar_inputs': searchbar_inputs,
            'searchbar_groupby': searchbar_groupby,
            'sortby': sortby,
            'groupby': groupby,
            'search_in': search_in,
            'search': search,
            'filterby': filterby,
        })
        return values
