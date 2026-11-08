def migrate(cr, version):
    """Los presupuestos que ya existian se emitieron antes de tener estado:
    quedan como aprobados (un administrador puede reabrirlos)."""
    cr.execute("UPDATE retana_budget SET state = 'approved'")
