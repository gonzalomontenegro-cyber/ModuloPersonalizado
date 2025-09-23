from odoo import models, fields, api
import requests
import logging

_logger = logging.getLogger(__name__)


class BoletaComuna(models.Model):
    _name = 'boleta.comuna'
    _description = 'Comuna'
    _rec_name = 'nombre'

    nombre = fields.Char(string="Nombre", required=True)
    boleta_ids = fields.One2many('boleta.honorarios', 'comuna_id', string="Boletas Asociadas")
    _sql_constraints = [
    ('nombre_unique', 'unique(nombre)', 'El nombre de la comuna debe ser único.'),
]



class BoletaHonorarios(models.Model):
    _inherit = 'boleta.honorarios'

    comuna_id = fields.Many2one('boleta.comuna', string="Comuna Asociada")

    @api.model
    def obtener_comunas_simpleapi(self):
        """Consume la API y guarda comunas nuevas en boleta.comuna"""
        url = "https://servicios.simpleapi.cl/api/bhe/listarComunas"

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            comunas = response.json()

            for comuna in comunas:
                nombre_comuna = comuna.get("nombre", "").strip()
                if nombre_comuna:
                    existing = self.env['boleta.comuna'].search([('nombre', '=', nombre_comuna)], limit=1)
                    if not existing:
                        self.env['boleta.comuna'].create({'nombre': nombre_comuna})

            _logger.info("Comunas cargadas correctamente desde SimpleAPI")

        except Exception as e:
            _logger.error("Error al obtener comunas desde SimpleAPI: %s", e)
            raise UserError(f"Error al obtener comunas: {e}")

    def agrupar_boletas_por_comuna(self):
        """Asigna las boletas emitidas a su comuna correspondiente"""
        self.obtener_comunas_simpleapi()  # Asegurarse de tener comunas actualizadas

        todas_boletas = self.env['boleta.honorarios'].search([('state', '=', 'emitted')])

        for boleta in todas_boletas:
            nombre_comuna = boleta.receptor_comuna.strip() if boleta.receptor_comuna else None
            if not nombre_comuna:
                continue

            comuna = self.env['boleta.comuna'].search([('nombre', '=', nombre_comuna)], limit=1)
            if comuna:
                boleta.comuna_id = comuna.id
