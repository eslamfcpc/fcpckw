# # -*- coding: utf-8 -*-
from odoo import models, fields, api

class AppointmentCreate(models.Model):
    _inherit = 'medical.appointment'

    no_invoice = fields.Boolean(string='Invoice exempt',default=False)
    state = fields.Selection([('draft', 'Draft'),('done', 'Done'),('shifted','Shfited'),('cancel','Canceled')])

    # @api.model
    # def create(self,vals):
    #     print("S")
    #     vals['name'] = self.env['ir.sequence'].next_by_code('medical.appointment') or 'APT'
    #     result = super(AppointmentCreate, self).create(vals)
    #     return result
	

