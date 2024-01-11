from odoo import http
from odoo.http import request


class KzmInstanceRequestController(http.Controller):
    @http.route('/my/kzm_instance_requests', auth='user', type='http', methods=['GET', 'POST'], website=True)
    # route for search by client and by url and by state
    def my_kzm_instance_requests(self, partner_id=None, url=None, state=None, **kw):
        user = request.env.user
        domain = [('create_uid', '=', user.id)]
        if partner_id:
            try:
                domain.append(('partner_id', '=', int(partner_id)))
            except:
                return request.not_found()
        if url:
            print("URL")
            domain.append(('url', '=', url))
        if state:
            print("STATE")
            domain.append(('state', '=', state))
        instances = request.env['kzm.instance.request'].search(domain)
        return request.render('kzm_instance_request.my_kzm_request_template', {'instances': instances})

    # route for grouping by state
    @http.route('/my/kzm_instance_requests', auth='user', type='http', website=True)
    def my_kzm_instance_requests_group_by_state(self, group_by_state=None, **kw):
        user = request.env.user

        domain = [('tl_user_id', '=', user.id)]

        requests = request.env['kzm.instance.request'].search(domain)

        grouped_data = []
        if group_by_state:
            grouped_data = request.env['kzm.instance.request'].read_group(
                domain,
                fields=['state'],
                groupby=['state'],
                orderby='state',
                lazy=False
            )
        print(grouped_data)
        return request.render('kzm_instance_request.template_my_kzm_instance_requests', {'requests': requests, 'grouped_data': grouped_data})

    # route for deleting instance request by request id
    @http.route('/my/delete_kzm_instance_request/<int:request_id>', auth='user', type='http', methods=['POST'], csrf=False, website=True)
    def delete_kzm_instance_request(self, request_id, **kw):
        user = request.env.user

        instance_request = request.env['kzm.instance.request'].sudo().browse(request_id)
        if not instance_request:
            return request.redirect('/my/kzm_instance_requests')
        instance_request.unlink()
        return request.redirect('/my/kzm_instance_requests')

    # route for create instance request automatically set to soumise state
    @http.route('/create_instance', auth='user', type="http", methods=['POST'], csrf=False)
    def create_instance_request(self, cpu=None, ram=None, disk=None, url=None,limit_date=None, treat_date=None, treat_duration=None):
        user = request.env.user
        instance_creation = {
            'cpu':cpu,
            'ram':ram,
            'disk':disk,
            'url':url,
            'state': 'Soumise',
            'limit_date': limit_date,
            'treat_date': treat_date,
            'treat_duration': treat_duration,
            'odoo_id': request.env['odoo.version'].search([('name', '=', '16.0')]).id
        }
        request.env['kzm.instance.request'].create(instance_creation)
        return request.redirect('/my/kzm_instance_requests')
        
