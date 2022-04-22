# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'Saudi HR Health information',
    'summary': """Saudi HR Health information """,
    'description': """
        Employee Health Information like Height, weight, Blood group etc.
    """,
    'author': 'erp-bank.',
    'website': 'http://www.erp-bank.com',
    'category': 'HR',
    'version': '1.0',
    'license': 'OPL-1',
    'depends': ['saudi_hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_views.xml',
    ],
    'demo': ['demo/demo.xml'],
    'images': [],
    "price": 0.0,
    "currency": "EUR",
    'installable': True,
    'application': True,
    'auto_install': False,
}
