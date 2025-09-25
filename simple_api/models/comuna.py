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
        """Sincroniza comunas desde la API externa de SimpleAPI (listarComunas)."""
        self.ensure_one()
        base_url, api_key, timeout = self._get_simpleapi_settings()
        url = f"{base_url}/bhe/listarComunas"

        headers_base = {'Accept': 'application/json'}
        attempts = []

        api_key_clean = (api_key or '').strip()
        if not api_key_clean:
            attempts.append({'name': 'no_auth', 'headers': headers_base.copy()})
        else:
            # CAMBIO: Priorizar Authorization tal cual (como en boleta_honorarios.py)
            # 1) Authorization tal cual - MÉTODO PRINCIPAL
            h_as_is = headers_base.copy()
            h_as_is['Authorization'] = api_key_clean
            attempts.append({'name': 'auth_direct', 'headers': h_as_is})

            # 2) x-api-key como alternativa
            h_x = headers_base.copy()
            h_x['x-api-key'] = api_key_clean
            attempts.append({'name': 'x-api-key', 'headers': h_x})

            # 3) Authorization: Bearer <token> como último recurso
            if not api_key_clean.lower().startswith('bearer '):
                h_bearer = headers_base.copy()
                h_bearer['Authorization'] = f"Bearer {api_key_clean}"
                attempts.append({'name': 'auth_bearer', 'headers': h_bearer})

        last_exc = None
        processed_total = 0
        for att in attempts:
            name = att['name']
            headers = att['headers']
            try:
                _logger.info('Solicitando comunas a %s (modo=%s, auth_preview=%s)', url, name, headers.get('Authorization') or headers.get('x-api-key') or '<none>')
                response = requests.get(url, headers=headers, timeout=timeout)
            except Exception as e:
                _logger.exception('Error en request (modo=%s): %s', name, e)
                last_exc = e
                continue

            _logger.info('Modo=%s HTTP=%s', name, response.status_code)
            if response.status_code == 200:
                try:
                    data = response.json()
                except Exception as e:
                    _logger.exception('JSON inválido en respuesta: %s', e)
                    raise UserError(_('Respuesta de SimpleAPI no es JSON válido: %s') % e)

                if isinstance(data, dict):
                    comunas = data.get('comunas') or data.get('data') or data.get('results') or []
                elif isinstance(data, list):
                    comunas = data
                else:
                    comunas = []

                processed = 0
                for item in comunas:
                    codigo = item.get('id') or item.get('codigo') or item.get('code') or False
                    nombre = item.get('nombre') or item.get('comuna') or item.get('name') or False
                    if not nombre:
                        _logger.warning('Elemento comunas sin nombre: %s', item)
                        continue

                    vals = {'name': nombre}
                    if codigo:
                        vals['codigo'] = str(codigo)

                    comuna_existente = self.search([('codigo', '=', vals.get('codigo'))], limit=1) if vals.get('codigo') else self.search([('name', '=', nombre)], limit=1)
                    if comuna_existente:
                        comuna_existente.write(vals)
                    else:
                        self.create(vals)
                    processed += 1
                    processed_total += 1

                _logger.info('Sincronización de comunas completada (modo=%s). Procesadas: %s', name, processed)
                return True

            if response.status_code in (401, 403):
                _logger.warning('Modo %s no autorizado (HTTP %s). Intentando siguiente método si existe.', name, response.status_code)
                last_exc = UserError(_('Error al obtener comunas desde SimpleAPI: %s') % response.status_code)
                continue

            _logger.warning('Modo %s respuesta inesperada HTTP %s: %s', name, response.status_code, (response.text or '')[:300])
            last_exc = UserError(_('Error al obtener comunas desde SimpleAPI: %s') % response.status_code)

        if isinstance(last_exc, Exception):
            raise last_exc
        raise UserError(_('No se pudo sincronizar comunas: respuesta desconocida de la API.'))