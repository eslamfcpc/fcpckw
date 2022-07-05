from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError


class MedicalConfig(models.Model):
    _name = 'medical.config'

    def _default_sale_journal(self):
        return self.env['account.journal'].search \
            ([('type', '=', 'general')],
             limit=1)

    def generate_pos_journal(self, company):
        for pos_config in self:
            if pos_config.journal_id:
                continue
            pos_journal = self.env['account.journal'].search([('company_id', '=', company.id), ('code', '=', 'POSS')])
            if not pos_journal:
                pos_journal = self.env['account.journal'].create({
                    'type': 'general',
                    'name': 'Point of Sale',
                    'code': 'POSS',
                    'company_id': company.id,
                    'sequence': 20
                })
            pos_config.write({'journal_id': pos_journal.id})

    journal_id = fields.Many2one(
        'account.journal', string='commission Journal',
        domain=[('type', '=', 'general')],
        help="Accounting journal used to post POS session journal entries and POS invoice payments.",
        # default=_default_sale_journal,
        ondelete='restrict')

    name = fields.Char(string='Configuration Name', index=True, required=True, help="An internal identification of the config.")



