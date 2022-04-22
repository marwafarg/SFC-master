# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "Saudi HR Branch",
    'summary': """ Middle East Human Resource """,
    'description': """
            Middle East Human Resource Groups Configuration
        """,
    'author': 'erp-bank.',
    'website': 'http://www.erp-bank.com',
    'category': 'HR',
    'version': '1.0',
    'sequence': 20,
    'license': 'OPL-1',
    'depends': ['hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_branch_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/office_demo.xml',
    ],
    'images': [
        'static/description/main_screen.jpg'
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
