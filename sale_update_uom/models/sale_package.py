# -*- coding: utf-8 -*-

from odoo import models, fields, api
# from datetime import datetime, timedelta
import pandas as pd

import datetime

class SalePackage(models.Model):
    _inherit = 'sale.order'
    _description = 'Package Field'



    @api.model
    def create(self, vals):
        price_list = self.env['product.pricelist'].search([('id', '=', vals['pricelist_id'])])
        if price_list.package == True:
            x = 0
            for p in range(vals['order_line'][0][2]['product_uom_qty']) :
                y = vals['days_between']
                first = vals['start_appoint']
                new_date = pd.to_datetime(first) + pd.DateOffset(days=x)
                appointment = self.env['medical.appointment']
                appointment.create({'patient_id':1,
                                    'appointment_date': new_date,
                                    'appointment_end': new_date,
                                    'consultations_id':vals['order_line'][0][2]['product_id'],
                                    'doctor_id':vals['doctor_id'],
                                    })
                x = x + y
        return super(SalePackage, self).create(vals)