# -*- coding: utf-8 -*-
from odoo import api, models

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
