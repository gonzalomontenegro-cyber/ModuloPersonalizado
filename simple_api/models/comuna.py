from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging
import requests

_logger = logging.getLogger(__name__)

class BoletaComuna(models.Model):
    _name = 'boleta.comuna'
    _description = 'Comuna para Boletas de Honorarios'

    codigo = fields.Char(string='Código', index=True)
    name = fields.Char(string='Nombre', required=True, index=True)

    boleta_ids = fields.One2many(
        'boleta.honorarios', 'comuna_id',
        string='Boletas'
    )

    boletas_count = fields.Integer(string='Cantidad de boletas', compute='_compute_boletas_count')

    _sql_constraints = [
        ('codigo_unique', 'unique(codigo)', 'El código de la comuna debe ser único.'),
    ]

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

    def _get_simpleapi_settings(self):
        """Obtiene parámetros de configuración para SimpleAPI desde ir.config_parameter"""
        icp = self.env['ir.config_parameter'].sudo()
        base_url = icp.get_param('boleta_honorarios.simpleapi_base_url') or 'https://servicios.simpleapi.cl/api'
        api_key = icp.get_param('boleta_honorarios.simpleapi_api_key') or False
        timeout = int(icp.get_param('boleta_honorarios.simpleapi_timeout') or 30)
        return base_url.rstrip('/'), api_key, timeout

    def sync_comunas(self):
        """Sincroniza comunas desde la API externa de SimpleAPI (listarComunas).
        Puede ser invocado desde un botón o por un cron.
        """
        self.ensure_one()
        base_url, api_key, timeout = self._get_simpleapi_settings()
        url = f"{base_url}/bhe/listarComunas"

        headers = {'Accept': 'application/json'}
        if api_key:
            headers['Authorization'] = f'Bearer {api_key}'

        try:
            _logger.info('Solicitando comunas a %s', url)
            response = requests.get(url, headers=headers, timeout=timeout)
            if response.status_code != 200:
                _logger.error('Error al consumir API comunas. Código: %s - %s', response.status_code, response.text)
                raise UserError(_('Error al obtener comunas desde SimpleAPI: %s') % response.status_code)

            data = response.json()

            # La API podría responder directamente una lista o un objeto con clave 'comunas' o 'data'.
            if isinstance(data, dict):
                comunas = data.get('comunas') or data.get('data') or data.get('results') or []
            elif isinstance(data, list):
                comunas = data
            else:
                comunas = []

            processed = 0
            for item in comunas:
                # Soportar objetos con 'id' y 'nombre' o con 'codigo' y 'comuna' etc.
                codigo = item.get('id') or item.get('codigo') or item.get('code') or False
                nombre = item.get('nombre') or item.get('comuna') or item.get('name') or False
                if not nombre:
                    _logger.warning('Elemento comunas sin nombre: %s', item)
                    continue

                vals = {'name': nombre}
                if codigo:
                    vals['codigo'] = str(codigo)

                existing = self.search([('codigo', '=', vals.get('codigo'))], limit=1) if vals.get('codigo') else self.search([('name', '=', nombre)], limit=1)
                if existing:
                    existing.write(vals)
                else:
                    self.create(vals)
                processed += 1

            _logger.info('Sincronización de comunas completada. Procesadas: %s', processed)
            return True
        except Exception as e:
            _logger.exception('Error en sync_comunas: %s', e)
            raise UserError(_('Error al sincronizar comunas: %s') % e)
