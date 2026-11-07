# -*- coding: utf-8 -*-
from . import models


def post_init_hook(env):
    """Solo al instalar: una actualizacion posterior no debe volver a cambiar la moneda."""
    env['retana.data.import.helper'].set_company_currency()
