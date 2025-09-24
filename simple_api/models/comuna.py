from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class BoletaComuna(models.Model):
    _name = 'boleta.comuna'
    _description = 'Comuna para Boletas de Honorarios'

    name = fields.Char(string='Nombre', required=True, index=True)
    
    boleta_ids = fields.One2many(
        'boleta.honorarios', 'comuna_id',
        string='Boletas'
    )

    boletas_count = fields.Integer(
        string='Cantidad de Boletas',
        compute='_compute_boletas_count'
    )

    _sql_constraints = [
        ('boleta_comuna_name_uniq', 'unique(name)', 'La comuna ya existe.'),
    ]

    @api.model
    def get_or_create_by_name(self, name):
        """Devuelve la comuna por nombre (case-insensitive). Si no existe, la crea.
        Retorna recordset vacío si name is falsy."""
        if not name:
            return self.browse()
        name = name.strip()
        comuna = self.search([('name', 'ilike', name)], limit=1)
        if comuna:
            return comuna
        try:
            comuna = self.sudo().create({'name': name})
            return comuna
        except Exception as e:
            _logger.error('Error creando comuna %s: %s', name, e)
            return self.browse()

    @api.depends('boleta_ids')
    def _compute_boletas_count(self):
        for comuna in self:
            comuna.boletas_count = len(comuna.boleta_ids)

    @api.model
    def agrupar_boletas_por_comuna(self):
        """Recorre boletas sin comuna y las asocia según su nombre de comuna."""
        Boleta = self.env['boleta.honorarios']
        boletas = Boleta.search([('comuna_id', '=', False)])
        _logger.info('Agrupar %s boletas sin comuna', len(boletas))
        boletas._associate_comuna()
        return True
