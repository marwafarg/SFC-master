# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': "HR Dependent",
    'summary': "HR Dependent",
    'description': """
        Allow specific user to add dependents""",
    'author': 'erp-bank.',
    'website': 'http://www.erp-bank.com',
    'category': 'HR',
    'version': '1.0',
    'license': 'OPL-1',
    'depends': ['saudi_hr', 'res_documents'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/saudi_hr_dependent.xml',
        ],
    'demo': ['demo/demo.xml'],
    'images': [],
    "price": 30.0,
    "currency": "EUR",
    'installable': True,
    'auto_install': False,
}
