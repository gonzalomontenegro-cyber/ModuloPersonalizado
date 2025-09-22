from odoo import models, fields

class Comuna(models.Model):
    _name = 'boleta.comuna'
    _description = 'Comuna Chilena'

    name = fields.Char('Nombre de la Comuna', required=True)
    region = fields.Selection([
        ('1', 'Tarapacá'), ('2', 'Antofagasta'), ('3', 'Atacama'), ('4', 'Coquimbo'),
        ('5', 'Valparaíso'), ('6', "O'Higgins"), ('7', 'Maule'), ('8', 'Biobío'),
        ('9', 'Araucanía'), ('10', 'Los Lagos'), ('11', 'Aysén'), ('12', 'Magallanes'),
        ('13', 'Metropolitana'), ('14', 'Los Ríos'), ('15', 'Arica y Parinacota'), ('16', 'Ñuble')
    ], string='Región', required=True)
