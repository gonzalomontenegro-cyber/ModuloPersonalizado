# -*- coding: utf-8 -*-
# from odoo import http


# class SimpleApi(http.Controller):
#     @http.route('/simple_api/simple_api', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/simple_api/simple_api/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('simple_api.listing', {
#             'root': '/simple_api/simple_api',
#             'objects': http.request.env['simple_api.simple_api'].search([]),
#         })

#     @http.route('/simple_api/simple_api/objects/<model("simple_api.simple_api"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('simple_api.object', {
#             'object': obj
#         })

