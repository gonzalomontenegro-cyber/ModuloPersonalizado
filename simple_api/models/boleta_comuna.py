from odoo import models, fields

class BoletaComuna(models.Model):
    _name = 'boleta.comuna'
    _description = 'Comunas para Boletas'

    name = fields.Char('Nombre Comuna', required=True)