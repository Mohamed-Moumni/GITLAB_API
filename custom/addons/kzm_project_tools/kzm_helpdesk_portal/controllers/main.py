# -*- coding: utf-8 -*-
import datetime
from dateutil.relativedelta import relativedelta
from werkzeug.exceptions import NotFound
from odoo import http
from odoo.http import request
from odoo.addons.website_form.controllers.main import WebsiteForm
from odoo.addons.portal.controllers.portal import get_records_pager, CustomerPortal

class WebsiteForm(WebsiteForm):

    @http.route('''/helpdesk/<model("helpdesk.team", "[('use_website_helpdesk_form','=',True)]"):team>/submit''',
                type='http', auth="public", website=True)
    def website_helpdesk_form(self, team, **kwargs):
        default_values = {}
        if request.env.user.partner_id != request.env.ref('base.public_partner'):
            default_values['name'] = request.env.user.partner_id.name
            default_values['email'] = request.env.user.partner_id.email
            default_values['subscription_id'] = request.env['sale.subscription'].sudo().search([('stage_id.id', '=', '2'),('partner_id.name', '=',request.env.user.partner_id.name)])
            #default_values['ticket_type_id'] = request.env['helpdesk.ticket.type'].sudo().search([])
        print("default", default_values)

        return request.render("website_helpdesk_form.ticket_submit", {'team': team, 'default_values': default_values})


class sale_subscription(http.Controller):

    @http.route(['/my/subscription/<int:account_id>/',
                 '/my/subscription/<int:account_id>/<string:uuid>'], type='http', auth="public", website=True)
    def subscription(self, account_id, uuid='', message='', message_class='', **kw):
        account_res = request.env['sale.subscription']
        if uuid:
            account = account_res.sudo().browse(account_id)
            if uuid != account.uuid:
                raise NotFound()
            if request.uid == account.partner_id.user_id.id:
                account = account_res.browse(account_id)
        else:
            account = account_res.browse(account_id)
        services = request.env['sale.subscription.service'].search([('subscription_id', '=', account.id)])
        acquirers = list(request.env['payment.acquirer'].search([
            ('website_published', '=', True),
            ('registration_view_template_id', '!=', False),
            ('token_implemented', '=', True)]))
        acc_pm = account.payment_token_id
        part_pms = account.partner_id.payment_token_ids
        display_close = account.template_id.sudo().user_closable and not account.in_progress
        is_follower = request.env.user.partner_id.id in [follower.partner_id.id for follower in account.message_follower_ids]
        active_plan = account.template_id.sudo()
        periods = {'daily': 'days', 'weekly': 'weeks', 'monthly': 'months', 'yearly': 'years'}
        if account.recurring_rule_type != 'weekly':
            rel_period = relativedelta(datetime.datetime.today(), account.recurring_next_date)
            missing_periods = getattr(rel_period, periods[account.recurring_rule_type]) + 1
        else:
            delta = datetime.date.today() - account.recurring_next_date
            missing_periods = delta.days / 7
        dummy, action = request.env['ir.model.data'].get_object_reference('sale_subscription', 'sale_subscription_action')
        values = {
            'account': account,
            'services': services,
            'template': account.template_id.sudo(),
            'display_close': display_close,
            'is_follower': is_follower,
            'close_reasons': request.env['sale.subscription.close.reason'].search([]),
            'missing_periods': missing_periods,
            'payment_mode': active_plan.payment_mode,
            'user': request.env.user,
            'acquirers': acquirers,
            'acc_pm': acc_pm,
            'part_pms': part_pms,
            'is_salesman': request.env['res.users'].sudo(request.uid).has_group('sales_team.group_sale_salesman'),
            'action': action,
            'message': message,
            'message_class': message_class,
            'change_pm': kw.get('change_pm') != None,
            'pricelist': account.pricelist_id.sudo(),
            'submit_class':'btn btn-primary mb8 mt8 float-right',
            'submit_txt':'Pay Subscription',
            'bootstrap_formatting':True,
            'return_url':'/my/subscription/' + str(account_id) + '/' + str(uuid),
        }

        history = request.session.get('my_subscriptions_history', [])
        values.update(get_records_pager(history, account))
        return request.render("sale_subscription.subscription", values)

    payment_succes_msg = 'message=Thank you, your payment has been validated.&message_class=alert-success'
    payment_fail_msg = 'message=There was an error with your payment, please try with another payment method or contact us.&message_class=alert-danger'