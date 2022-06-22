# -*- coding: utf-8 -*-
{
    'name': "sale_update_uom",

    'summary': """
        Update Unit Of Measure And Qunatity In Stock Move""",

    'description': """
     Update Unit Of Measure And Qunatity In Stock Move
    """,

    'author': "Iteration",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale','basic_hms','account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/state_appointment.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
