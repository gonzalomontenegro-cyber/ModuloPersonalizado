from odoo import models, fields

class ResComuna(models.Model):
    _name = 'res.comuna'
    _description = 'Comunas de Chile'

    name = fields.Char('Nombre', required=True)
    region_id = fields.Many2one('res.region', string='Región')  # asumiendo que tienes modelo región
