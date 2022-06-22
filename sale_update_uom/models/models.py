# # -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class sale_update_uom(models.Model):
#     _inherit = 'stock.move'
#     _description = 'Get Unit'

#     # Ovverride Field In stock To Compute 
#     product_uom = fields.Many2one('uom.uom', "UoM", required=True, domain="[('category_id', '=', product_uom_category_id)]", compute='calc_unit_of_measure')
    

#     # Get Unit Of Measure And Quantity From Sale Order 
#     @api.model
#     def calc_unit_of_measure(self):
#         for rec in self:
#             sale_order = self.env['sale.order'].search([('name', '=', rec.origin)])
#             if sale_order:
#                 print(sale_order.ids[0])
#                 sale_order_id = self.env['sale.order.line'].search([('order_id', '=', sale_order.ids[0])])
#                 rec.product_uom = sale_order_id.product_uom.id
#                 rec.product_uom_qty = sale_order_id.product_uom_qty
#             else:
#                 rec.product_uom = rec.product_uom
                
