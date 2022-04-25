# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _, exceptions


class medical_physician(models.Model):
    _name = "medical.physician"
    _description = 'medical physician'
    _rec_name = 'partner_id'

    partner_id = fields.Many2one('res.partner', 'Physician', required=True)
    institution_partner_id = fields.Many2one('res.partner', domain=[('is_institution', '=', True)],
                                             string='Institution')
    code = fields.Char('Id')
    info = fields.Text('Extra Info')
    commission_Percentage = fields.Float(string='Commission', default=0)
    duration = fields.Float(string='Duration(hh: mm)', required=True)

    @api.constrains('commission_Percentage')
    def _check_percentage(self):
        for r in self:
            if r.commission_Percentage > 100:
                raise exceptions.ValidationError("The Commission Percentage  must be less than or equal to 100")

    @api.onchange('commission_Percentage')
    def _verify_valid_dates(self):
        if self.commission_Percentage > 100:
            return {
                'warning': {
                    'title': "Validation Error",
                    'message': "The Percentage amount must be less than or equal to 100",
                }
            }
