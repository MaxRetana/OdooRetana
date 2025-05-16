from odoo import http
from odoo.http import request

class HomeViewController(http.Controller):

    @http.route('/web/homeview', type='http', auth='user', website=True)
    def home_view(self, **kw):
        apps = request.env['ir.ui.menu'].search([('parent_id', '=', False)])
        app_list = [{'id': app.id, 'name': app.name, 'icon': 'fa fa-cube'} for app in apps]
        return request.render('mi_home_view.home_view_tag', {'apps': app_list})
