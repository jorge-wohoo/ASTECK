# -*- coding: utf-8 -*-
from odoo import http

# class infile(http.Controller):
#     @http.route('/infile/infile/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/infile/infile/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('infile.listing', {
#             'root': '/infile/infile',
#             'objects': http.request.env['infile.infile'].search([]),
#         })

#     @http.route('/infile/infile/objects/<model("infile.infile"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('infile.object', {
#             'object': obj
#         })