# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class PateintUpdate(models.Model):
    _inherit = 'medical.patient'
    _description = 'hospital.update'

    phone = fields.Char(String="Phone", related='patient_id.phone', store=True)
    civil_number = fields.Char(String="Civil Number")
    customer_file_number = fields.Char(String="Customer File Number", required=True, copy=False, readonly=True,
                           index=True, default=lambda self: _('New'))
    relative_person = fields.Many2one('res.partner', related='patient_id.relative_partner_id', store=True, string="Relative Person")
    relationship = fields.Char(related='patient_id.relationship', store=True, String="Relationship")
    civil_attachment = fields.Many2many('ir.attachment', string="Civil Attachment", required=True)



    # Sequence patient Function    
    @api.model
    def create(self, vals):
        if vals.get('customer_file_number', _('New')) == _('New'):
            vals['customer_file_number'] = self.env['ir.sequence'].next_by_code('patient.sequence') or _('New')
        result = super(PateintUpdate, self).create(vals)
        return result