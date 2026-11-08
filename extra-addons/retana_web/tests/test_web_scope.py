from odoo.tests.common import HttpCase, tagged


@tagged('post_install', '-at_install')
class TestWebScope(HttpCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Partner = cls.env['res.partner']
        cls.client_a = Partner.create({'name': 'Cliente Alfa', 'is_retana_customer': True})
        cls.client_b = Partner.create({'name': 'Cliente Beta', 'is_retana_customer': True})
        cls.records = {}
        for key, client in (('a', cls.client_a), ('b', cls.client_b)):
            building = cls.env['retana.buildings'].create({'name': f'Obra {key}', 'client_id': client.id})
            cls.records[key] = {
                'building': building,
                'budget': cls.env['retana.budget'].create({'client_id': client.id, 'building_id': building.id, 'title': f'Presupuesto {key}'}),
                'downpayment': cls.env['retana.downpayment'].create({'client_id': client.id, 'building_id': building.id, 'amount': 50.0}),
            }
        portal = cls.env.ref('base.group_portal')
        Users = cls.env['res.users'].with_context(no_reset_password=True)
        cls.customer_user = Users.create({
            'name': 'Portal Alfa', 'login': 'portal_alfa', 'password': 'portal_alfa',
            'partner_id': cls.client_a.id, 'group_ids': [(6, 0, [portal.id])],
        })
        staff_group = cls.env.ref('retana_web.group_retana_portal_staff')
        cls.staff_user = Users.create({
            'name': 'Personal portal', 'login': 'portal_staff', 'password': 'portal_staff',
            'group_ids': [(6, 0, [portal.id, staff_group.id])],
        })
        cls.stranger_user = Users.create({
            'name': 'Portal sin cliente', 'login': 'portal_stranger', 'password': 'portal_stranger',
            'group_ids': [(6, 0, [portal.id])],
        })

    def _get(self, login, path):
        self.authenticate(login, login)
        return self.url_open(path, allow_redirects=False)

    def test_customer_lists_only_own_records(self):
        body = self._get('portal_alfa', '/retana/budgets').text
        self.assertIn('Presupuesto a', body)
        self.assertNotIn('Presupuesto b', body)
        body = self._get('portal_alfa', '/retana/buildings').text
        self.assertIn('Obra a', body)
        self.assertNotIn('Obra b', body)

    def test_customer_cannot_open_other_client_records(self):
        own, other = self.records['a'], self.records['b']
        for kind, route in (('budget', 'budgets'), ('downpayment', 'downpayments'), ('building', 'buildings')):
            self.assertEqual(self._get('portal_alfa', f'/retana/{route}/{own[kind].id}').status_code, 200, kind)
            self.assertEqual(self._get('portal_alfa', f'/retana/{route}/{other[kind].id}').status_code, 404, kind)
        self.assertEqual(self._get('portal_alfa', f'/retana/budgets/{other["budget"].id}/report').status_code, 404)

    def test_customer_cannot_use_bulk_creation(self):
        self.assertNotEqual(self._get('portal_alfa', '/retana/downpayments/bulk').status_code, 200)
        self.assertNotIn('/retana/downpayments/bulk', self._get('portal_alfa', '/retana/downpayments').text)

    def test_staff_portal_user_has_full_access(self):
        body = self._get('portal_staff', '/retana/budgets').text
        self.assertIn('Presupuesto a', body)
        self.assertIn('Presupuesto b', body)
        self.assertEqual(self._get('portal_staff', '/retana/downpayments/bulk').status_code, 200)
        self.assertEqual(self._get('portal_staff', f'/retana/budgets/{self.records["b"]["budget"].id}').status_code, 200)

    def test_portal_user_without_client_or_staff_group_sees_nothing(self):
        for path in ('/retana/budgets', '/retana/downpayments', '/retana/buildings', '/retana/downpayments/bulk'):
            response = self._get('portal_stranger', path)
            self.assertNotEqual(response.status_code, 200, path)
            self.assertNotIn('Presupuesto a', response.text, path)
        self.assertNotEqual(self._get('portal_stranger', f'/retana/budgets/{self.records["a"]["budget"].id}').status_code, 200)

    def test_staff_group_does_not_make_user_internal(self):
        self.assertFalse(self.staff_user._is_internal())
        self.assertTrue(self.staff_user.has_group('base.group_portal'))
