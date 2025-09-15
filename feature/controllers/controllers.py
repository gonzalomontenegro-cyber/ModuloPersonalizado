# -*- coding: utf-8 -*-
# from odoo import http


# class Feature(http.Controller):
#     @http.route('/feature/feature', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/feature/feature/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('feature.listing', {
#             'root': '/feature/feature',
#             'objects': http.request.env['feature.feature'].search([]),
#         })

#     @http.route('/feature/feature/objects/<model("feature.feature"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('feature.object', {
#             'object': obj
#         })

