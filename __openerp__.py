# -*- coding: utf-8 -*-
{
    'name': "secondary_purchase_order",

    'summary': """
        secondary_purchase_order""",

    'description': """
        secondary_purchase_order
    """,

    'author': "Warren Castro",
    'website': "http://www.recicladorasanmiguel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'purchase'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'templates.xml',
        'data/order_sequence.xml',
        'secondary_purchase_order_report.xml',
        'views/report_tiquete_compra_secondary.xml',
        'views/report_produccion_semanal.xml',
        'views/report_produccion_diaria.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',

    ],
}
