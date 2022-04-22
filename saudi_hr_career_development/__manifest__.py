# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': "Middle East Human Resource Career Development",
    'summary': """ Middle East Human Resource Career Development """,
    'description': """ Middle East Human Resource Career Development """,
    'author': 'erp-bank.',
    'website': 'http://www.erp-bank.com',
    'category': 'Human Resources',
    'version': '1.0',
    'sequence': 20,
    'license': 'OPL-1',
    'depends': ['base', 'saudi_hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_career_development_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': ['demo/demo.xml'],
    'images': [],
    'price': 0.0,
    'installable': True,
    'auto_install': False,
    'application': False,
}
