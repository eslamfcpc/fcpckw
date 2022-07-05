# -*- coding: utf-8 -*-
# from odoo import http


# class SaleUpdateUom(http.Controller):
#     @http.route('/sale_update_uom/sale_update_uom', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sale_update_uom/sale_update_uom/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('sale_update_uom.listing', {
#             'root': '/sale_update_uom/sale_update_uom',
#             'objects': http.request.env['sale_update_uom.sale_update_uom'].search([]),
#         })

#     @http.route('/sale_update_uom/sale_update_uom/objects/<model("sale_update_uom.sale_update_uom"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sale_update_uom.object', {
#             'object': obj
#         })
