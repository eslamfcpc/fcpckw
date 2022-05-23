# -*- coding: utf-8 -*-
{
    'name': "hospital",

    'summary': """
        Hospital Update App""",

    'description': """
        Hospital Update App
    """,

    'author': "Moaz Nabil",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','basic_hms'],

    # always loaded
    'data': [
        'views/patient_view_update.xml',
        'data/file_number_seq.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
