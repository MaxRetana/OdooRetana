from odoo import http
from odoo.http import request
from odoo.exceptions import AccessDenied
from datetime import date, timedelta


class RetanaBillsWebsiteController(http.Controller):

    def _safe_filename(self, value, fallback):
        name = (value or fallback or 'documento').replace('/', '-').replace('\\', '-')
        return name.strip() or fallback

    def _download_report(self, action_xmlid, records, filename):
        if not records:
            return request.not_found()

        report_service = request.env['ir.actions.report'].sudo()
        pdf_content, _ = report_service._render_qweb_pdf(action_xmlid, records.ids)
        headers = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', str(len(pdf_content))),
            ('Content-Disposition', 'attachment; filename="%s"' % filename),
        ]
        return request.make_response(pdf_content, headers=headers)

    def _parse_page(self, page, kwargs):
        try:
            page_from_kwargs = kwargs.get('page')
            if page_from_kwargs is not None:
                page = int(page_from_kwargs)
            else:
                page = int(page or 1)
        except (TypeError, ValueError):
            page = 1
        return page if page > 0 else 1

    def _group_records(self, records, group_by, get_label):
        if group_by == 'none':
            return [{'label': '', 'records': records}]

        groups = []
        current_label = None
        current_records = []

        for record in records:
            label = get_label(record) or '-'
            if label != current_label:
                if current_records:
                    groups.append({'label': current_label, 'records': current_records})
                current_label = label
                current_records = [record]
            else:
                current_records.append(record)

        if current_records:
            groups.append({'label': current_label, 'records': current_records})

        return groups

    def _ensure_portal_user(self):
        user = request.env.user
        try:
            is_portal = user.has_group('base.group_portal') or user.has_group('base.group_system')
        except ValueError:
            is_portal = False

        if not is_portal:
            raise AccessDenied('Solo usuarios de portal pueden acceder a esta pagina.')

    @http.route('/', type='http', auth='user', website=True)
    def retana_home(self, **kwargs):
        self._ensure_portal_user()
        budget_model = request.env['retana.budget'].sudo()
        downpayment_model = request.env['retana.downpayment'].sudo()
        building_model = request.env['retana.buildings'].sudo()

        return request.render(
            'retana_web.retana_web_home',
            {
                'home_budget_count': budget_model.search_count([]),
                'home_downpayment_count': downpayment_model.search_count([]),
                'home_building_count': building_model.search_count([]),
                'home_recent_budgets': budget_model.search([], order='date desc, id desc', limit=5),
                'home_recent_downpayments': downpayment_model.search([], order='date desc, id desc', limit=5),
                'home_recent_buildings': building_model.search([], order='id desc', limit=5),
            },
        )

    @http.route(['/retana/budgets', '/retana/budgets/page/<int:page>'], type='http', auth='user', website=True)
    def retana_budgets(self, page=1, **kwargs):
        self._ensure_portal_user()

        search = (kwargs.get('search') or '').strip()
        filter_by = kwargs.get('filter_by') or 'all'
        group_by = kwargs.get('group_by') or 'none'
        page = self._parse_page(page, kwargs)
        step = 20

        filter_options = [
            ('all', 'Todos'),
            ('today', 'Hoy'),
            ('this_week', 'Semana actual'),
            ('this_month', 'Mes actual'),
        ]
        group_options = [
            ('none', 'Sin agrupar'),
            ('client', 'Cliente'),
            ('budget_type', 'Tipo de Presupuesto'),
            ('building', 'Obra'),
            ('date', 'Fecha'),
        ]

        if filter_by not in dict(filter_options):
            filter_by = 'all'
        if group_by not in dict(group_options):
            group_by = 'none'

        domain = []
        if search:
            domain += [
                '|', '|', '|',
                ('name', 'ilike', search),
                ('title', 'ilike', search),
                ('client_id.name', 'ilike', search),
                ('building_id.name', 'ilike', search),
            ]

        today = date.today()
        if filter_by == 'today':
            domain.append(('date', '=', today))
        elif filter_by == 'this_week':
            week_start = today - timedelta(days=today.weekday())
            week_end = week_start + timedelta(days=6)
            domain += [('date', '>=', week_start), ('date', '<=', week_end)]
        elif filter_by == 'this_month':
            month_start = today.replace(day=1)
            if today.month == 12:
                next_month_start = today.replace(year=today.year + 1, month=1, day=1)
            else:
                next_month_start = today.replace(month=today.month + 1, day=1)
            domain += [('date', '>=', month_start), ('date', '<', next_month_start)]

        order_map = {
            'none': 'date desc, id desc',
            'client': 'client_id asc, date desc, id desc',
            'budget_type': 'budget_type_id asc, date desc, id desc',
            'building': 'building_id asc, date desc, id desc',
            'date': 'date desc, id desc',
        }
        budget_model = request.env['retana.budget'].sudo()
        budget_total = budget_model.search_count(domain)
        budget_pager = request.website.pager(
            url='/retana/budgets',
            total=budget_total,
            page=page,
            step=step,
            scope=5,
            url_args={
                'search': search,
                'filter_by': filter_by,
                'group_by': group_by,
            },
        )
        budgets = budget_model.search(
            domain,
            order=order_map[group_by],
            limit=step,
            offset=budget_pager['offset'],
        )

        budget_groups = self._group_records(
            budgets,
            group_by,
            lambda b: {
                'client': b.client_id.name,
                'budget_type': b.budget_type_id.name,
                'building': b.building_id.name,
                'date': str(b.date) if b.date else '-',
            }.get(group_by, ''),
        )

        return request.render(
            'retana_web.retana_web_budgets',
            {
                'budgets': budgets,
                'budget_groups': budget_groups,
                'budget_search': search,
                'budget_filter_by': filter_by,
                'budget_group_by': group_by,
                'budget_filter_options': filter_options,
                'budget_group_options': group_options,
                'budget_pager': budget_pager,
                'budget_total': budget_total,
            },
        )

    @http.route('/retana/budgets/<int:budget_id>', type='http', auth='user', website=True)
    def retana_budget_detail(self, budget_id, **kwargs):
        self._ensure_portal_user()
        budget = request.env['retana.budget'].sudo().browse(budget_id)
        if not budget.exists():
            return request.not_found()

        return request.render(
            'retana_web.retana_web_budget_detail',
            {
                'budget': budget,
            },
        )

    @http.route('/retana/budgets/<int:budget_id>/report', type='http', auth='user', website=True)
    def retana_budget_report_download(self, budget_id, **kwargs):
        self._ensure_portal_user()
        budget = request.env['retana.budget'].sudo().browse(budget_id)
        if not budget.exists():
            return request.not_found()

        filename = '%s.pdf' % self._safe_filename('%s' % (budget.title), 'Presupuesto')
        return self._download_report('retana_bills.action_report_retana_budget', budget, filename)

    @http.route(['/retana/downpayments', '/retana/downpayments/page/<int:page>'], type='http', auth='user', website=True)
    def retana_downpayments(self, page=1, **kwargs):
        self._ensure_portal_user()

        search = (kwargs.get('search') or '').strip()
        filter_by = kwargs.get('filter_by') or 'all'
        group_by = kwargs.get('group_by') or 'none'
        page = self._parse_page(page, kwargs)
        step = 20

        filter_options = [
            ('all', 'Todos'),
            ('current_week', 'Semana actual'),
        ]
        group_options = [
            ('none', 'Sin agrupar'),
            ('name', 'Nombre'),
            ('client', 'Cliente'),
            ('concept', 'Concepto'),
            ('building', 'Obra'),
        ]

        if filter_by not in dict(filter_options):
            filter_by = 'all'
        if group_by not in dict(group_options):
            group_by = 'none'

        domain = []
        if search:
            domain += [
                '|', '|', '|',
                ('name', 'ilike', search),
                ('client_id.name', 'ilike', search),
                ('concept_id.name', 'ilike', search),
                ('building_id.name', 'ilike', search),
            ]

        if filter_by == 'current_week':
            today = date.today()
            week_start = today - timedelta(days=today.weekday())
            week_end = week_start + timedelta(days=6)
            domain += [('date', '>=', week_start), ('date', '<=', week_end)]

        order_map = {
            'none': 'date desc, id desc',
            'name': 'name asc, date desc, id desc',
            'client': 'client_id asc, date desc, id desc',
            'concept': 'concept_id asc, date desc, id desc',
            'building': 'building_id asc, date desc, id desc',
        }
        downpayment_model = request.env['retana.downpayment'].sudo()
        downpayment_total = downpayment_model.search_count(domain)
        downpayment_pager = request.website.pager(
            url='/retana/downpayments',
            total=downpayment_total,
            page=page,
            step=step,
            scope=5,
            url_args={
                'search': search,
                'filter_by': filter_by,
                'group_by': group_by,
            },
        )
        downpayments = downpayment_model.search(
            domain,
            order=order_map[group_by],
            limit=step,
            offset=downpayment_pager['offset'],
        )

        downpayment_groups = self._group_records(
            downpayments,
            group_by,
            lambda d: {
                'name': d.name,
                'client': d.client_id.name,
                'concept': d.concept_id.name,
                'building': d.building_id.name,
            }.get(group_by, ''),
        )

        return request.render(
            'retana_web.retana_web_downpayments',
            {
                'downpayments': downpayments,
                'downpayment_groups': downpayment_groups,
                'downpayment_search': search,
                'downpayment_filter_by': filter_by,
                'downpayment_group_by': group_by,
                'downpayment_filter_options': filter_options,
                'downpayment_group_options': group_options,
                'downpayment_pager': downpayment_pager,
                'downpayment_total': downpayment_total,
            },
        )

    @http.route('/retana/downpayments/<int:downpayment_id>', type='http', auth='user', website=True)
    def retana_downpayment_detail(self, downpayment_id, **kwargs):
        self._ensure_portal_user()
        downpayment = request.env['retana.downpayment'].sudo().browse(downpayment_id)
        if not downpayment.exists():
            return request.not_found()

        return request.render(
            'retana_web.retana_web_downpayment_detail',
            {
                'downpayment': downpayment,
            },
        )

    @http.route('/retana/downpayments/<int:downpayment_id>/report', type='http', auth='user', website=True)
    def retana_downpayment_report_download(self, downpayment_id, **kwargs):
        self._ensure_portal_user()
        downpayment = request.env['retana.downpayment'].sudo().browse(downpayment_id)
        if not downpayment.exists():
            return request.not_found()

        filename = '%s.pdf' % self._safe_filename('Anticipo_%s' % (downpayment.name or downpayment_id), 'Anticipo')
        return self._download_report('retana_bills.action_report_retana_downpayment', downpayment, filename)

    @http.route('/retana/downpayments/report/batch', type='http', auth='user', website=True, methods=['POST'])
    def retana_downpayments_batch_report_download(self, **post):
        self._ensure_portal_user()

        selected_raw_ids = request.httprequest.form.getlist('downpayment_ids')
        selected_ids = []
        for raw_id in selected_raw_ids:
            try:
                selected_id = int(raw_id)
            except (TypeError, ValueError):
                continue
            if selected_id > 0:
                selected_ids.append(selected_id)

        if not selected_ids:
            return request.redirect('/retana/downpayments')

        downpayments = request.env['retana.downpayment'].sudo().browse(selected_ids).exists()
        if not downpayments:
            return request.redirect('/retana/downpayments')

        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        week_thursday = week_start + timedelta(days=3)

        filename = '%s.pdf' % self._safe_filename(
            'Anticipos_semana_%s_%s' % (week_thursday.day, week_thursday.year),
            'Anticipos_semana',
        )
        return self._download_report('retana_bills.action_report_retana_downpayment', downpayments, filename)

    @http.route(['/retana/buildings', '/retana/buildings/page/<int:page>'], type='http', auth='user', website=True)
    def retana_buildings(self, page=1, **kwargs):
        self._ensure_portal_user()

        search = (kwargs.get('search') or '').strip()
        filter_by = kwargs.get('filter_by') or 'active'
        group_by = kwargs.get('group_by') or 'none'
        page = self._parse_page(page, kwargs)
        step = 20

        filter_options = [
            ('all', 'Todas'),
            ('active', 'Activas'),
            ('inactive', 'Archivadas'),
        ]
        group_options = [
            ('none', 'Sin agrupar'),
            ('client', 'Cliente'),
            ('active', 'Estado'),
        ]

        if filter_by not in dict(filter_options):
            filter_by = 'active'
        if group_by not in dict(group_options):
            group_by = 'none'

        domain = []
        if search:
            domain += ['|', ('name', 'ilike', search), ('client_id.name', 'ilike', search)]

        if filter_by == 'active':
            domain.append(('active', '=', True))
        elif filter_by == 'inactive':
            domain.append(('active', '=', False))

        order_map = {
            'none': 'name asc, id desc',
            'client': 'client_id asc, name asc, id desc',
            'active': 'active desc, name asc, id desc',
        }
        building_model = request.env['retana.buildings'].sudo()
        building_total = building_model.search_count(domain)
        building_pager = request.website.pager(
            url='/retana/buildings',
            total=building_total,
            page=page,
            step=step,
            scope=5,
            url_args={
                'search': search,
                'filter_by': filter_by,
                'group_by': group_by,
            },
        )
        buildings = building_model.search(
            domain,
            order=order_map[group_by],
            limit=step,
            offset=building_pager['offset'],
        )

        building_groups = self._group_records(
            buildings,
            group_by,
            lambda b: {
                'client': b.client_id.name,
                'active': 'Activas' if b.active else 'Archivadas',
            }.get(group_by, ''),
        )

        return request.render(
            'retana_web.retana_web_buildings',
            {
                'buildings': buildings,
                'building_groups': building_groups,
                'building_search': search,
                'building_filter_by': filter_by,
                'building_group_by': group_by,
                'building_filter_options': filter_options,
                'building_group_options': group_options,
                'building_pager': building_pager,
                'building_total': building_total,
            },
        )

    @http.route('/retana/buildings/<int:building_id>', type='http', auth='user', website=True)
    def retana_building_detail(self, building_id, **kwargs):
        self._ensure_portal_user()
        building = request.env['retana.buildings'].sudo().browse(building_id)
        if not building.exists():
            return request.not_found()

        return request.render(
            'retana_web.retana_web_building_detail',
            {
                'building': building,
            },
        )

    @http.route('/retana/buildings/<int:building_id>/report', type='http', auth='user', website=True)
    def retana_building_report_download(self, building_id, **kwargs):
        self._ensure_portal_user()
        building = request.env['retana.buildings'].sudo().browse(building_id)
        if not building.exists():
            return request.not_found()

        downpayments = request.env['retana.downpayment'].sudo().search([
            ('building_id', '=', building.id),
        ], order='date asc, id asc')

        if not downpayments:
            return request.not_found()

        filename = '%s.pdf' % self._safe_filename('RelacionPagos_%s' % (building.name or building.id), 'RelacionPagos')
        return self._download_report('retana_bills.action_report_retana_building_downpayments', downpayments, filename)
