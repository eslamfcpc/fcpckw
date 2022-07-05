# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PackageField(models.Model):
    _inherit = 'product.pricelist'
    _description = 'Package Field'

    package = fields.Boolean(string="Is Backage", default=False)



class PackageFieldSale(models.Model):
    _inherit = 'sale.order'
    _description = 'Sale Package Field'

    package = fields.Boolean(string="Is Backage", related='pricelist_id.package')
    days_between = fields.Integer(string="Days Between")
    start_appoint = fields.Datetime(string="Start Appointment")
    doctor_id = fields.Many2one('medical.physician', string="Physician")