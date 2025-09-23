from odoo import models, fields

class BoletaComuna(models.Model):
    _name = 'boleta.comuna'
    _description = 'Comuna'

    name = fields.Char(string='Nombre', required=True)
