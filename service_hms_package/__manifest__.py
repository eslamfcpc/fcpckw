# -*- coding: utf-8 -*-
{
    'name': "Service Package HMS",

    'summary': """
        App Will Provide Service Package To basic_hms APP """,

    'description': """
        App Will Provide Service Package To basic_hms APP 
    """,

    'author': "Moaz Nabil",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'basic_hms', 'sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/views.xml',
        'views/price_list_override.xml',
        # 'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
