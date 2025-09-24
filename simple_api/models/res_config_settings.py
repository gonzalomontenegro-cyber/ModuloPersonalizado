from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    simpleapi_api_key = fields.Char(
        string='SimpleAPI Key',
        config_parameter='boleta_honorarios.simpleapi_api_key',
        default='5858-R580-6392-2845-5641',
        help='API Key proporcionada por SimpleAPI'
    )
    
    simpleapi_base_url = fields.Char(
        string='SimpleAPI Base URL',
        config_parameter='boleta_honorarios.simpleapi_base_url',
        default='https://servicios.simpleapi.cl/api',
        help='URL base de la API de SimpleAPI'
    )
    
    simpleapi_timeout = fields.Integer(
        string='Timeout (segundos)',
        config_parameter='boleta_honorarios.simpleapi_timeout',
        default=30,
        help='Tiempo límite para las peticiones HTTP'
    )

    