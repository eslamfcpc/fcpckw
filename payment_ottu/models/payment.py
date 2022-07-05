# coding: utf-8

import json
import logging
import pprint

import dateutil.parser
import pytz
from werkzeug import urls

from odoo import api, fields, models, _
from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.addons.payment_ottu.controllers.main import OttuController
from odoo.tools.float_utils import float_compare


_logger = logging.getLogger(__name__)


class AcquirerOttu(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[
        ('knet', 'KNET'),
        ('cybersource', 'Cybersource'),
        ('omannet', 'Omannet')
    ], ondelete={'knet': 'set default', 'cybersource': 'set default', 'omannet': 'set default'})
    ottu_gateway_url = fields.Char('Gateway URL', groups='base.group_user')
    ottu_gateway_code = fields.Char('Gateway Code',groups='base.group_user')

    def _get_feature_support(self):
        """Get advanced feature support by provider.

        Each provider should add its technical in the corresponding
        key for the following features:
            * fees: support payment fees computations
            * authorize: support authorizing payment (separates
                         authorization and capture)
            * tokenize: support saving payment data in a payment.tokenize
                        object
        """
        res = super(AcquirerOttu, self)._get_feature_support()
        res['fees'].append('ottu')
        return res

    # --------------------------------------------------
    # Ottu Payment acquirer methods
    # --------------------------------------------------

    @api.model
    def _get_ottu_urls(self, environment):
        """ Ottu URLS """
        base_url = self.get_base_url()
        return urls.url_join(base_url, OttuController._redirect_url)

    def ottu_compute_fees(self, amount, currency_id, country_id):
        """ Compute Ottu fees.

            :param float amount: the amount to pay
            :param integer country_id: an ID of a res.country, or None. This is
                                       the customer's country, to be compared to
                                       the acquirer company country.
            :return float fees: computed fees
        """
        if not self.fees_active:
            return 0.0
        country = self.env['res.country'].browse(country_id)
        if country and self.company_id.sudo().country_id.id == country.id:
            percentage = self.fees_dom_var
            fixed = self.fees_dom_fixed
        else:
            percentage = self.fees_int_var
            fixed = self.fees_int_fixed
        fees = (percentage / 100.0 * amount + fixed) / (1 - percentage / 100.0)
        return fees

    def ottu_form_generate_values(self, values):
        base_url = self.get_base_url()
        ottu_tx_values = ({
            "amount": round(float(values['amount']), 3),
            "currency_code": values['currency'] and values['currency'].name or 'USD',
            "language":"en",
            "gateway_url": self.ottu_gateway_url,
            "gateway_code": self.ottu_gateway_code,
            "order_no": values['reference'],
            "customer_email": values.get('partner_email'),
            "disclosure_url": urls.url_join(base_url, OttuController._disclosure_url),
            "redirect_url": urls.url_join(base_url, "/payment/process/"),
        })
        return ottu_tx_values

    def ottu_get_form_action_url(self):
        self.ensure_one()
        environment = 'prod' if self.state == 'enabled' else 'test'
        return self._get_ottu_urls(environment)

    # --------------------------------------------------
    # KNET FORM RELATED METHODS
    # --------------------------------------------------

    def knet_compute_fees(self, amount, currency_id, country_id):
        return self.ottu_compute_fees(amount, currency_id, country_id)

    def knet_form_generate_values(self, values):
        return self.ottu_form_generate_values(values)

    def knet_get_form_action_url(self):
        return  self.ottu_get_form_action_url()

    # --------------------------------------------------
    # Cybersource FORM RELATED METHODS
    # --------------------------------------------------

    def cybersource_compute_fees(self, amount, currency_id, country_id):
        return self.ottu_compute_fees(amount, currency_id, country_id)

    def cybersource_form_generate_values(self, values):
        return self.ottu_form_generate_values(values)

    def cybersource_get_form_action_url(self):
        return  self.ottu_get_form_action_url()

    # --------------------------------------------------
    # Omannet FORM RELATED METHODS
    # --------------------------------------------------

    def omannet_compute_fees(self, amount, currency_id, country_id):
        return self.ottu_compute_fees(amount, currency_id, country_id)

    def omannet_form_generate_values(self, values):
        base_url = self.get_base_url()
        omannet_tx_values = ({
            "amount": values['amount'],
            "currency_code": values['currency'] and values['currency'].name or 'USD',
            "language":"en",
            "gateway_url": self.ottu_gateway_url,
            "gateway_code": self.ottu_gateway_code,
            "order_no": values['reference'].replace('-', ''),
            "customer_email": values.get('partner_email'),
            "disclosure_url": urls.url_join(base_url, OttuController._disclosure_url),
            "redirect_url": urls.url_join(base_url, "/payment/process/"),
            "extra_order_no": values['reference']
        })
        return omannet_tx_values

    def omannet_get_form_action_url(self):
        return  self.ottu_get_form_action_url()

class TxOttu(models.Model):
    _inherit = 'payment.transaction'

    ottu_result = fields.Char('Result')
    ottu_gateway_name = fields.Char('Gateway Name')
    ottu_transaction_id = fields.Char('Transaction ID')
    ottu_payment_id = fields.Char('Payment ID')
    ottu_auth_id = fields.Char('Auth ID')
    ottu_track_id = fields.Char('Track ID')

    # --------------------------------------------------
    # Ottu Payment acquirer methods
    # --------------------------------------------------

    @api.model
    def _ottu_form_get_tx_from_data(self, data):
        reference = data.get('order_no')
        if not reference:
            error_msg = _('Ottu: received data with missing reference (%s)') % (reference)
            _logger.info(error_msg)
            raise ValidationError(error_msg)

        # find tx -> @TDENOTE use txn_id ?
        if data.get('extra') and data["extra"].get("order_no"):
            txs = self.env['payment.transaction'].search([('reference', '=', data["extra"]["order_no"])])
        elif reference:
            txs = self.env['payment.transaction'].search([('reference', '=', reference)])
        if not txs or len(txs) > 1:
            error_msg = 'Ottu: received data for reference %s' % (reference)
            if not txs:
                error_msg += '; no order found'
            else:
                error_msg += '; multiple order found'
            _logger.info(error_msg)
            raise ValidationError(error_msg)
        return txs[0]

    def _ottu_form_get_invalid_parameters(self, data):
        invalid_parameters = []
        _logger.info('Received a notification from Ottu')

        if data.get('currency_code') != self.currency_id.name:
            invalid_parameters.append(('Currency Code', data.get('currency_code'), self.currency_id.name))
        if not data.get('result'):
            invalid_parameters.append(('Result', data.get('result')))
        if not data.get('gateway_name'):
            invalid_parameters.append(('Gateway Name', data.get('gateway_name')))
        if not data.get('reference_number'):
            invalid_parameters.append(('Reference Number', data.get('reference_number')))
        return invalid_parameters

    def _knet_form_validate(self, data):
        status = data.get('gateway_response').get('result')
        former_tx_state = self.state
        res = {
            'acquirer_reference': data.get('gateway_response').get('ref')
        }

        date = fields.Datetime.now()
        if status in ['CAPTURED']:
            self._set_transaction_done()
            res.update({
                "date":date,
                "ottu_result":data.get('result'), 
                "ottu_gateway_name":data.get('gateway_name'),
                "ottu_transaction_id":data.get('gateway_response').get('tranid'), 
                "ottu_payment_id":data.get('gateway_response').get('paymentid'), 
                "ottu_auth_id":data.get('gateway_response').get('auth'),
                "ottu_track_id":data.get('gateway_response').get('trackid')
            })
            if self.state == 'done' and self.state != former_tx_state:
                _logger.info('Validated Ottu payment for tx %s: set as done' % (self.reference))
                return self.write(res)
            return True
        elif status in ['NOT CAPTURED']:
            res.update({
                "date":date,
                "ottu_result":data.get('result'), 
                "ottu_gateway_name":data.get('gateway_name'),
                "ottu_transaction_id":data.get('gateway_response').get('tranid'), 
                "ottu_payment_id":data.get('gateway_response').get('paymentid'), 
                "ottu_auth_id":data.get('gateway_response').get('auth'),
                "ottu_track_id":data.get('gateway_response').get('trackid')
            })
            state_message = 'Received %s notification for Ottu payment %s: set as pending' % (status, self.reference)
            res.update(state_message=state_message)
            return self.write(res)
        else:
            if(status in ['CANCELED']):
                res.update({
                    "ottu_result":data.get('result'), 
                    "ottu_gateway_name":data.get('gateway_name'),
                    "ottu_transaction_id":data.get('gateway_response').get('tranid'), 
                    "ottu_payment_id":data.get('gateway_response').get('paymentid'),
                    "ottu_track_id":data.get('gateway_response').get('trackid')

                })
                error = 'Received %s notification for Ottu payment %s: set as cancelled' % (self.reference, status)
            else:
                error = 'Received unrecognized status for Ottu payment %s: %s, set as error' % (self.reference, status)
            error += "\n" + pprint.pformat(data)
            res.update(state_message=error)
            self._set_transaction_cancel()
            if self.state == 'cancel' and self.state != former_tx_state:
                _logger.info(error)
                return self.write(res)
            return False

    def _cybersource_form_validate(self, data):
        status = data.get('gateway_response').get('decision')
        former_tx_state = self.state
        res = {
            'acquirer_reference': data.get('reference_number')
        }
        date = fields.Datetime.now()

        if status in ['ACCEPT']:
            self._set_transaction_done()
            res.update({
                "date":date,
                "ottu_result":data.get('result'), 
                "ottu_gateway_name":data.get('gateway_name'),
                "ottu_transaction_id":data.get('gateway_response').get('transaction_id'), 
                "ottu_auth_id":data.get('gateway_response').get('auth_code'),
                "ottu_track_id":data.get('gateway_response').get('req_reference_number')
            })
            if self.state == 'done' and self.state != former_tx_state:
                _logger.info('Validated Ottu payment for tx %s: set as done' % (self.reference))
                return self.write(res)
            return True
        else:
            if(status in ['CANCELED']):
                res.update({
                    "ottu_result":data.get('result'), 
                    "ottu_gateway_name":data.get('gateway_name'),
                    "ottu_track_id":data.get('gateway_response').get('req_reference_number')
                })
                error = 'Received %s notification for Ottu payment %s: set as cancelled' % (self.reference, status)
            else:
                error = 'Received unrecognized status for Ottu payment %s: %s, set as error' % (self.reference, status)
            
            res.update(state_message=error)
            self._set_transaction_cancel()
            if self.state == 'cancel' and self.state != former_tx_state:
                _logger.info(error)
                return self.write(res)
            return False

    def _omannet_form_validate(self, data):
        status = data.get('gateway_response').get('result')
        former_tx_state = self.state
        res = {
            'acquirer_reference': data.get('gateway_response').get('ref')
        }

        date = fields.Datetime.now()
        if status in ['CAPTURED']:
            self._set_transaction_done()
            res.update({
                "date":date,
                "ottu_result":data.get('result'), 
                "ottu_gateway_name":data.get('gateway_name'),
                "ottu_transaction_id":data.get('gateway_response').get('tranid'), 
                "ottu_payment_id":data.get('gateway_response').get('paymentid'), 
                "ottu_auth_id":data.get('gateway_response').get('auth'),
                "ottu_track_id":data.get('gateway_response').get('trackid')
            })
            if self.state == 'done' and self.state != former_tx_state:
                _logger.info('Validated Ottu payment for tx %s: set as done' % (self.reference))
                return self.write(res)
            return True
        else:
            if(status in ['CANCELED']):
                res.update({
                    "ottu_result":data.get('result'), 
                    "ottu_gateway_name":data.get('gateway_name'),
                    "ottu_transaction_id":data.get('gateway_response').get('tranid'), 
                    "ottu_payment_id":data.get('gateway_response').get('paymentid'),
                    "ottu_track_id":data.get('gateway_response').get('trackid')

                })
                error = 'Received %s notification for Ottu payment %s: set as cancelled' % (self.reference, status)
            else:
                error = 'Received unrecognized status for Ottu payment %s: %s, set as error' % (self.reference, status)
            res.update(state_message=error)
            self._set_transaction_cancel()
            if self.state == 'cancel' and self.state != former_tx_state:
                _logger.info(error)
                return self.write(res)
            return False

    def _ottu_form_validate(self, data):
        if(self.acquirer_id.provider == "knet"):
            return self._knet_form_validate(data)
        elif(self.acquirer_id.provider == "cybersource"):
            return self._cybersource_form_validate(data)
        elif(self.acquirer_id.provider == "omannet"):
            return self._omannet_form_validate(data)
        else:
            return False

