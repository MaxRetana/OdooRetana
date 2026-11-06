# -*- coding: utf-8 -*-
"""Genera los CSV de data/ a partir de una base con los datos de Retana.

Se ejecuta SOBRE UNA COPIA de la base (asigna ids externos a los registros):

    odoo-bin shell -d <copia> --addons-path=... < export_data.py

Variable de entorno RETANA_EXPORT_DIR: carpeta de salida (por defecto ../data).
"""
import csv
import os

MODULE = 'retana_data_import'
OUT = os.environ.get('RETANA_EXPORT_DIR') or os.path.join(os.path.dirname(os.path.abspath('__file__')), 'data')

# modelo -> (dominio, campos a excluir, nombre del archivo)
MODELS = [
    ('res.partner', ['|', ('id', '>=', 29), ('id', '=', 1)], {'user_id', 'commercial_partner_id', 'company_id', 'parent_id', 'is_published', 'employee', 'trust',
                                                                        'autopost_bills', 'ignore_abnormal_invoice_date',
                                                                        'ignore_abnormal_invoice_amount'}),
    ('product.template', [], {'company_id', 'is_favorite'}),
    ('retana.type.res.partner', [], set()),
    ('retana.budget.type', [], set()),
    ('retana.downpayment.type.concept', [], set()),
    ('retana.buildings', [], set()),
    ('retana.budget', [], set()),
    ('retana.budget.line', [], set()),
    ('retana.downpayment', [], set()),
    ('retana.sent.wh', [], set()),
    ('retana.company.info', [], set()),
]
MAGIC = {'id', 'create_uid', 'write_uid', 'create_date', 'write_date', 'display_name', 'parent_path',
         'access_token', 'message_main_attachment_id', 'signup_token', 'signup_type', 'signup_expiration'}
SKIP_PREFIX = ('message_', 'activity_', 'website_message', 'rating_')
OK_TYPES = {'char', 'text', 'html', 'boolean', 'integer', 'float', 'monetary', 'date', 'datetime',
            'selection', 'many2one', 'many2many', 'binary'}
# modelos relacionales que si podemos referenciar por xmlid
STD_TARGETS = {'product.product', 'res.country', 'res.country.state', 'res.currency', 'uom.uom', 'product.category',
               'account.tax', 'res.partner.industry', 'res.partner.category', 'res.lang'}


def assign_xmlids(model, records):
    existing = {r.res_id: r for r in env['ir.model.data'].search([('model', '=', model), ('res_id', 'in', records.ids)])}
    for rec in records:
        if rec.id in existing:
            continue
        env['ir.model.data'].create({'module': MODULE, 'name': '%s_%s' % (model.replace('.', '_'), rec.id),
                                     'model': model, 'res_id': rec.id, 'noupdate': True})


def export_fields(model, excluded):
    Model = env[model]
    names, dropped = [], []
    exported_models = {m for m, _d, _e in MODELS}
    for name, f in Model._fields.items():
        if name in MAGIC or name in excluded or name.startswith(SKIP_PREFIX):
            continue
        if not f.store or f.type not in OK_TYPES or (f.compute and not f.inverse) or f.related:
            continue
        if f.type in ('many2one', 'many2many'):
            if f.comodel_name not in exported_models | STD_TARGETS:
                dropped.append('%s -> %s' % (name, f.comodel_name))
                continue
        if f.type == 'binary' and name != 'image_1920':
            continue
        names.append(name)
    return names, dropped


# ids externos fijos para los registros que se crean a mano en data/*.xml
for model, name, dom in (('account.tax', 'tax_iva_16', [('name', '=', '16%'), ('type_tax_use', '=', 'sale')]),
                         ('uom.uom', 'uom_ml', [('name', '=', 'ml')])):
    cands = env[model].with_context(lang='en_US').search(dom)
    with_xmlid = set(env['ir.model.data'].search([('model', '=', model), ('res_id', 'in', cands.ids)]).mapped('res_id'))
    rec = cands.filtered(lambda r: r.id not in with_xmlid)[:1]  # el personalizado, no el estandar
    if rec:
        env['ir.model.data'].create({'module': MODULE, 'name': name, 'model': model, 'res_id': rec.id, 'noupdate': True})

# variantes: su xmlid se deriva del de la plantilla (ver models/retana_data_import_helper.py)
for tmpl in env['product.template'].with_context(active_test=False).search([]):
    var = tmpl.product_variant_id
    if var:
        env['ir.model.data'].create({'module': MODULE, 'name': 'product_product_%s' % tmpl.id, 'model': 'product.product',
                                     'res_id': var.id, 'noupdate': True})

for model, domain, excluded in MODELS:
    assign_xmlids(model, env[model].with_context(active_test=False).search(domain, order='id'))

for model, domain, excluded in MODELS:
    Model = env[model].with_context(lang='en_US', active_test=False)
    records = Model.search(domain, order='id')
    names, dropped = export_fields(model, excluded)
    fields_list = ['id']
    for n in names:
        t = Model._fields[n].type
        fields_list.append(n + '/id' if t in ('many2one', 'many2many') else n)
    rows = [list(r) for r in records.export_data(fields_list)['datas']]
    # selection/boolean: valores internos en vez de etiquetas traducidas
    for i, n in enumerate(names, start=1):
        t = Model._fields[n].type
        if t == 'selection':
            for row, rec in zip(rows, records):
                row[i] = rec[n] or ''
        elif t == 'boolean':
            for row, rec in zip(rows, records):
                row[i] = 'True' if rec[n] else 'False'
    # quitar columnas totalmente vacias
    keep = [i for i in range(len(fields_list)) if i == 0 or any(r[i] not in ('', False, None) for r in rows)]
    path = os.path.join(OUT, model + '.csv')
    with open(path, 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh)
        w.writerow([fields_list[i] for i in keep])
        for r in rows:
            w.writerow([('' if r[i] in (False, None) else r[i]) for i in keep])
    print('%-34s %5d filas %3d columnas  descartados: %s' % (model, len(rows), len(keep), dropped))

env.cr.rollback()  # no persistimos los xmlids en la copia
