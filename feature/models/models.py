# -*- coding: utf-8 -*-

from odoo import models, fields, api


class my_learning(models.Model):
    _inherit = 'slide.channel' #herencia de modelo slide.channel
    #todo debajo de este comentario hace referencia al modelo de nuestro módulo
    _name = 'my_learning.my_learning'
    _description = 'my_learning.my_learning'
    nuevo_campo = fields.Char()