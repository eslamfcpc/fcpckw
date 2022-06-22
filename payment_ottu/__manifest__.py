# -*- coding: utf-8 -*-
{
    'name': "Ottu Payment Integrator",
    'category': 'Accounting/Payment Acquirers',
    'sequence': 400,
    'summary': "Payment Acquirer: Ottu Implementation",
    'description': """Ottu Payment Acquirer""",
    'author': "Ottu",
    'website': "https://www.ottu.com",
    'depends': ['account','sale','payment'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/payment_views.xml',
        'views/payment_ottu_templates.xml',
        'views/ottu_portal_templates.xml',
        'data/payment_acquirer_data.xml',
    ],
    'application': True,
    'post_init_hook': 'create_missing_journal_for_acquirers',
}
