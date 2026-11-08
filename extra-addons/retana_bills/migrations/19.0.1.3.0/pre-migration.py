def migrate(cr, version):
    """Las secuencias de presupuestos y anticipos se creaban desde el codigo, sin
    identificador externo. Se les asigna uno para que el XML las reconozca en vez
    de crear secuencias duplicadas."""
    for code, xmlid in (('retana.budget', 'seq_retana_budget'), ('retana.downpayment', 'seq_retana_downpayment')):
        cr.execute("SELECT id FROM ir_sequence WHERE code = %s ORDER BY id LIMIT 1", (code,))
        row = cr.fetchone()
        if not row:
            continue
        cr.execute("SELECT 1 FROM ir_model_data WHERE module = 'retana_bills' AND name = %s", (xmlid,))
        if not cr.fetchone():
            cr.execute(
                "INSERT INTO ir_model_data (module, name, model, res_id, noupdate) "
                "VALUES ('retana_bills', %s, 'ir.sequence', %s, true)",
                (xmlid, row[0]),
            )
