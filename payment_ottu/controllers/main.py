# -*- coding: utf-8 -*-

import json
import logging
import pprint

import requests
import werkzeug
from werkzeug import urls

from odoo import fields, http, _
from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.http import request
from odoo.exceptions import AccessError, MissingError
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo.addons.payment.controllers.portal import PaymentProcessing
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.addons.website_form.controllers.main import WebsiteForm

_logger = logging.getLogger(__name__)


class OttuController(http.Controller):
    _redirect_url = '/payment/ottu/redirect/'
    _disclosure_url = '/payment/ottu/disclosure/'

    def knet_validate_data(self, data, tx):
        res = False
        resp = data.get('gateway_response').get('result')
        if resp in ['CAPTURED']:
            _logger.info('KNET: validated data')
            res = request.env['payment.transaction'].sudo().form_feedback(data, 'ottu')
            if not res and tx:
                tx._set_transaction_error('Validation error occured. Please contact your administrator.')
        elif resp in ['NOT CAPTURED', 'CANCELED']:
            _logger.warning('KNET: answered NOT CAPTURED/CANCELED on data verification')
            res = request.env['payment.transaction'].sudo().form_feedback(data, 'ottu')
            if tx:
                tx._set_transaction_error('Invalid response from KNET. Please contact your administrator.')
        else:
            _logger.warning('KNET: unrecognized KNET answer, received %s instead of CAPTURED or NOT CAPTURED/CANCELED' % (resp))
            if tx:
                tx._set_transaction_error('Unrecognized error from KNET. Please contact your administrator.')
        return res

    def cybersource_validate_data(self, data, tx):
        res = False
        resp = data.get('gateway_response').get('decision')
        if resp in ['ACCEPT']:
            _logger.info('Cybersource: validated data')
            res = request.env['payment.transaction'].sudo().form_feedback(data, 'ottu')
            if not res and tx:
                tx._set_transaction_error('Validation error occured. Please contact your administrator.')
        elif resp in ['CANCEL']:
            _logger.warning('Cybersource: answered CANCEL on data verification')
            res = request.env['payment.transaction'].sudo().form_feedback(data, 'ottu')
            if tx:
                tx._set_transaction_error('Invalid response from Cybersource. Please contact your administrator.')
        else:
            _logger.warning('Cybersource: unrecognized Cybersource answer, received %s instead of CAPTURED or NOT CAPTURED/CANCELED' % (resp))
            if tx:
                tx._set_transaction_error('Unrecognized error from Cybersource. Please contact your administrator.')
        return res

    def omannet_validate_data(self, data, tx):
        res = False
        resp = data.get('gateway_response').get('result')
        if resp in ['CAPTURED']:
            _logger.info('Omannet: validated data')
            res = request.env['payment.transaction'].sudo().form_feedback(data, 'ottu')
            if not res and tx:
                tx._set_transaction_error('Validation error occured. Please contact your administrator.')
        elif resp in ['IPAY0100048 - Cancelled']:
            _logger.warning('Omannet: answered CANCELED on data verification')
            res = request.env['payment.transaction'].sudo().form_feedback(data, 'ottu')
            if tx:
                tx._set_transaction_error('Invalid response from Omannet. Please contact your administrator.')
        else:
            _logger.warning('Omannet: unrecognized Omannet answer, received %s instead of CAPTURED or NOT CAPTURED/CANCELED' % (resp))
            if tx:
                tx._set_transaction_error('Unrecognized error from Omannet. Please contact your administrator.')
        return res

    def ottu_validate_data(self, data):
        reference = data.get('order_no')
        tx = None
        if data.get('extra') and data["extra"].get("order_no"):
            tx = request.env['payment.transaction'].sudo().search([('reference', '=', data["extra"]["order_no"])])
        elif reference:
            tx = request.env['payment.transaction'].sudo().search([('reference', '=', reference)])
        if not tx:
            # we have seemingly received a notification for a payment that did not come from
            # odoo, acknowledge it otherwise ottu will keep trying
            _logger.warning('received notification for unknown payment reference')
            return False
        if(tx.acquirer_id.provider == "knet"):
            res = self.knet_validate_data(data, tx)
        elif(tx.acquirer_id.provider == "cybersource"):
            res = self.cybersource_validate_data(data, tx)
        elif(tx.acquirer_id.provider == "omannet"):
            res = self.omannet_validate_data(data, tx)
        else:
            _logger.warning('Ottu: unrecognized Ottu answer, received %s instead of CAPTURED or NOT CAPTURED/CANCELED' % (resp))
            if tx:
                tx._set_transaction_error('Unrecognized error from Ottu. Please contact your administrator.')
        return res

    @http.route('/payment/ottu/redirect', type="http", website=True, auth="public", csrf=False)
    def ottu_redirect(self, **kw):
        url = kw["gateway_url"]
        payload="{\n    \"amount\": \""+ kw["amount"] +"\",\n    \"currency_code\": \""+ kw["currency_code"] +"\",\n    \"language\": \"en\",\n    \"gateway_code\": \""+ kw["gateway_code"] +"\",\n    \"order_no\": \""+ kw["order_no"] +"\",\n    \"customer_email\": \""+ kw["customer_email"] +"\",\n    \"disclosure_url\": \""+ kw["disclosure_url"] +"\",\n    \"redirect_url\": \""+ kw["redirect_url"] +"\",\n    \"extra\": {\n        \"order_no\": \"S00074-13\"\n    }\n}"
        headers = {
          'Content-Type': 'application/json'
        }
        if(kw.get("extra_order_no")):
            payload="{\n    \"amount\": \""+ kw["amount"] +"\",\n    \"currency_code\": \""+ kw["currency_code"] +"\",\n    \"language\": \"en\",\n    \"gateway_code\": \""+ kw["gateway_code"] +"\",\n    \"order_no\": \""+ kw["order_no"] +"\",\n    \"customer_email\": \""+ kw["customer_email"] +"\",\n    \"disclosure_url\": \""+ kw["disclosure_url"] +"\",\n    \"redirect_url\": \""+ kw["redirect_url"] +"\",\n    \"extra\": {\n        \"order_no\": \""+ kw["extra_order_no"] +"\"\n    }\n}"
        else:
            payload="{\n    \"amount\": \""+ kw["amount"] +"\",\n    \"currency_code\": \""+ kw["currency_code"] +"\",\n    \"language\": \"en\",\n    \"gateway_code\": \""+ kw["gateway_code"] +"\",\n    \"order_no\": \""+ kw["order_no"] +"\",\n    \"customer_email\": \""+ kw["customer_email"] +"\",\n    \"disclosure_url\": \""+ kw["disclosure_url"] +"\",\n    \"redirect_url\": \""+ kw["redirect_url"] +"\"}"

        response = requests.request("POST", url, headers=headers, data=payload)
        data = response.json()
        logging.info('Redirect URL: %s', data)
        if(data.get("url")):
            return werkzeug.utils.redirect(data["url"])
        else:
            return werkzeug.utils.redirect('/payment/process')

    @http.route('/payment/ottu/disclosure/', type='json', auth="public", methods=['POST', 'GET'], csrf=False)
    def ottu_disclosure(self, **post):
        """ Ottu Disclosure """
        try:
            raw_body_data = http.request.jsonrequest
            _logger.info('Beginning Ottu Disclosure form_feedback with post data %s', pprint.pformat(raw_body_data))  # debug
            res = self.ottu_validate_data(raw_body_data)
        except ValidationError:
            _logger.exception('Unable to validate the Ottu payment')
        return ""

class CustomerPortalInherit(CustomerPortal):
    @http.route(['/my/orders/<int:order_id>'], type='http', auth="public", website=True)
    def portal_knet_order_page(self, order_id, report_type=None, access_token=None, message=False, download=False, **kw):
        try:
            order_sudo = self._document_check_access('sale.order', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        if report_type in ('html', 'pdf', 'text'):
            return self._show_report(model=order_sudo, report_type=report_type, report_ref='sale.action_report_saleorder', download=download)

        # use sudo to allow accessing/viewing orders for public user
        # only if he knows the private token
        # Log only once a day
        if order_sudo:
            # store the date as a string in the session to allow serialization
            now = fields.Date.today().isoformat()
            session_obj_date = request.session.get('view_quote_%s' % order_sudo.id)
            if session_obj_date != now and request.env.user.share and access_token:
                request.session['view_quote_%s' % order_sudo.id] = now
                body = _('Quotation viewed by customer %s', order_sudo.partner_id.name)
                _message_post_helper(
                    "sale.order",
                    order_sudo.id,
                    body,
                    token=order_sudo.access_token,
                    message_type="notification",
                    subtype_xmlid="mail.mt_note",
                    partner_ids=order_sudo.user_id.sudo().partner_id.ids,
                )

        values = self._order_get_page_view_values(order_sudo, access_token, **kw)
        values["payment_trans"] = values["sale_order"].transaction_ids.filtered(lambda l: l.state == "done")
        values['message'] = message

        return request.render('sale.sale_order_portal_template', values)

class WebsiteSaleFormInherit(WebsiteForm):
    @http.route(['/shop/confirmation'], type='http', auth="public", website=True, sitemap=False)
    def payment_confirmation_knet(self, **post):
        """ End of checkout process controller. Confirmation is basically seing
        the status of a sale.order. State at this point :

         - should not have any context / session info: clean them
         - take a sale.order id, because we request a sale.order and are not
           session dependant anymore
        """
        sale_order_id = request.session.get('sale_last_order_id')
        if sale_order_id:
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            payment_trans = order.transaction_ids.filtered(lambda l: l.state == "done")
            return request.render("website_sale.confirmation", {'order': order, "payment_trans":payment_trans})
        else:
            return request.redirect('/shop')