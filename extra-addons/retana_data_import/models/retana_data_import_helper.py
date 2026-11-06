# -*- coding: utf-8 -*-
import logging

from odoo import api, models

_logger = logging.getLogger(__name__)

MODULE = 'retana_data_import'


class RetanaDataImportHelper(models.AbstractModel):
    _name = 'retana.data.import.helper'
    _description = 'Utilidades de la importacion de datos de Retana'

    @api.model
    def register_product_variant_xmlids(self):
        """Registra el id externo de la variante de cada plantilla importada.

        Las lineas de presupuesto apuntan a product.product (la variante), que Odoo crea
        solo al importar la plantilla y por eso no tiene id externo en los CSV.
        Plantilla `product_template_N` -> variante `product_product_N`.
        """
        data = self.env['ir.model.data']
        templates = data.search([('module', '=', MODULE), ('model', '=', 'product.template'),
                                 ('name', '=like', 'product_template_%')])
        for xmlid in templates:
            template = self.env['product.template'].browse(xmlid.res_id).exists()
            variant = template.with_context(active_test=False).product_variant_id
            name = 'product_product_' + xmlid.name[len('product_template_'):]
            if variant and not data.search_count([('module', '=', MODULE), ('name', '=', name)]):
                data.create({'module': MODULE, 'name': name, 'model': 'product.product',
                             'res_id': variant.id, 'noupdate': True})

    @api.model
    def register_base_records(self):
        """Registra los ids externos de la unidad `ml`, el impuesto 16% y las secuencias.

        Si el registro ya existe en la base (p. ej. un impuesto 16% de venta creado a mano
        en produccion) se reutiliza; solo se crea cuando falta. Odoo no permite dos
        impuestos con el mismo nombre en la misma compania, por eso no van en un XML.
        """
        data = self.env['ir.model.data']

        def link(name, model, record):
            if not data.search_count([('module', '=', MODULE), ('name', '=', name)]):
                data.create({'module': MODULE, 'name': name, 'model': model,
                             'res_id': record.id, 'noupdate': True})

        def has_xmlid(model, record):
            return data.search_count([('model', '=', model), ('res_id', '=', record.id)])

        if not data.search_count([('module', '=', MODULE), ('name', '=', 'uom_ml')]):
            Uom = self.env['uom.uom'].with_context(active_test=False, lang='en_US')
            # el personalizado (sin id externo), no el `mL` estandar de Odoo
            custom = Uom.search([('name', '=', 'ml')]).filtered(lambda u: not has_xmlid('uom.uom', u))[:1]
            link('uom_ml', 'uom.uom', custom or Uom.create({'name': 'ml', 'relative_factor': 1}))

        if not data.search_count([('module', '=', MODULE), ('name', '=', 'tax_iva_16')]):
            company = self.env.ref('base.main_company')
            Tax = self.env['account.tax'].with_context(active_test=False, lang='en_US')
            tax = Tax.search([('name', '=', '16%'), ('type_tax_use', '=', 'sale'),
                              ('company_id', '=', company.id)], limit=1)
            if not tax:
                mexico = self.env.ref('base.mx')
                group = self.env['account.tax.group'].with_context(lang='en_US').search(
                    [('name', '=', 'Presupuestos Retana')], limit=1)
                group = group or self.env['account.tax.group'].create(
                    {'name': 'Presupuestos Retana', 'country_id': mexico.id})
                tax = Tax.create({'name': '16%', 'amount_type': 'percent', 'amount': 16,
                                  'type_tax_use': 'sale', 'tax_group_id': group.id,
                                  'country_id': mexico.id, 'company_id': company.id})
            link('tax_iva_16', 'account.tax', tax)

        # Secuencias: conservan la numeracion de Odoo 17 (proximo presupuesto: RB0025)
        Sequence = self.env['ir.sequence']
        for code, name, prefix, number_next in (
                ('retana.budget', 'Retana Budget Sequence', 'RB', 25),
                ('retana.downpayment', 'Retana Downpayment Sequence', 'RD', 1)):
            sequence = Sequence.search([('code', '=', code)], limit=1)
            if not sequence:
                Sequence.create({'name': name, 'code': code, 'prefix': prefix, 'padding': 4,
                                 'number_next': number_next, 'number_increment': 1, 'company_id': False})
            elif sequence.number_next_actual < number_next:
                sequence.number_next = number_next

    @api.model
    def set_company_currency(self):
        """Deja la moneda de la empresa en MXN, como estaba en Odoo 17.

        Los modelos de Retana usan la moneda de la empresa como moneda por defecto; en una base
        nueva de Odoo 19 es USD. Odoo no deja cambiarla si ya hay movimientos contables, en cuyo
        caso solo se avisa en el log y no se toca nada.
        """
        mxn = self.env.ref('base.MXN')
        company = self.env.ref('base.main_company')
        if company.currency_id == mxn:
            return
        if self.env['account.move'].sudo().search_count([('company_id', '=', company.id)]):
            _logger.warning('retana_data_import: la moneda de %s no se cambia a MXN porque ya tiene '
                            'asientos contables.', company.display_name)
            return
        mxn.active = True
        company.currency_id = mxn
