from psycopg2 import IntegrityError

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged
from odoo.tools import mute_logger


@tagged('post_install', '-at_install')
class TestHomeModel(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.menu = cls.env.ref('base.menu_administration')

    def test_menu_must_be_unique(self):
        self.env['home.home'].create({'name': 'A', 'menu_id': self.menu.id})
        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            self.env['home.home'].create({'name': 'B', 'menu_id': self.menu.id})

    def test_fa_icon_is_validated(self):
        with self.assertRaises(ValidationError):
            self.env['home.home'].create({'name': 'A', 'fa_icon': 'rocket<script>'})
        record = self.env['home.home'].create({'name': 'B', 'fa_icon': 'fa-rocket'})
        self.assertEqual(record.fa_icon, 'fa-rocket')

    def test_archived_shortcuts_are_hidden(self):
        record = self.env['home.home'].create({'name': 'A', 'menu_id': self.menu.id})
        record.active = False
        self.assertFalse(self.env['home.home'].search([('id', '=', record.id)]))
