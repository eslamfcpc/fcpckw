# -*- coding: utf-8 -*-
# from odoo import http


# class ServiceHmsPackage(http.Controller):
#     @http.route('/service_hms_package/service_hms_package', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/service_hms_package/service_hms_package/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('service_hms_package.listing', {
#             'root': '/service_hms_package/service_hms_package',
#             'objects': http.request.env['service_hms_package.service_hms_package'].search([]),
#         })

#     @http.route('/service_hms_package/service_hms_package/objects/<model("service_hms_package.service_hms_package"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('service_hms_package.object', {
#             'object': obj
#         })
