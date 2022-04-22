# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': "HR Sponsorship Transfer",
    'summary': """ Employee Sponsorship Transfer""",
    'description': """
        This module is useful when any expats candidate leave from other organization and hire on our organization at that time we need to change the sponsorship of candidate.
    """,
    'author': 'erp-bank.',
    'website': 'http://www.erp-bank.com',
    'category': 'Generic Modules/Human Resources',
    'version': '1.0',
    'license': 'OPL-1',
    'depends': ['saudi_hr', 'hr_recruitment'],
    'data': [
            'security/security.xml',
            'security/ir.model.access.csv',
            'data/email_template_view.xml',
            'views/hr_sponsorship_transfer_view.xml',
            ],
    'demo': ['demo/demo.xml'],
    'images': [
        'static/description/main_screen.jpg'
    ],
    "price": 0.0,
    "currency": "EUR",
    'installable': True,
    'application': True,
    'auto_install': False,
}
