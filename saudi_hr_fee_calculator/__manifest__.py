# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "Saudi HR Fee Calculator",
    'summary': """ Saudi HR Fee Calculator """,
    'description': """ Calculate fees based on employee """,
    'author': 'erp-bank.',
    'website': 'http://www.erp-bank.com',
    'category': 'Human Resources',
    'version': '1.0',
    'license': 'OPL-1',
    'depends': ['saudi_hr'],
    'data': [
            'security/ir.model.access.csv',
            'data/cron.xml',
            'views/emp_calculator_view.xml',
            'menu.xml',
    ],
    # only loaded in demonstration mode
    'demo': ['demo/demo.xml'],
    'installable': True,
    'auto_install': False,
}
