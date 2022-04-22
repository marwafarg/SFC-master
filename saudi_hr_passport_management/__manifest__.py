# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "Middle East Human Resource Passport Management",
    'summary': """
        Middle East Human Resource Passport Management""",

    'description': """
        Passport Management details.
    """,
    'author': 'erp-bank.',
    'website': 'http://www.erp-bank.com',
    'category': 'GR',
    'version': '1.0',
    'sequence': 20,
    'license': 'OPL-1',
    'depends': ['base', 'saudi_hr', 'saudi_hr_visa'],
    'data': [
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'data/passport_data.xml',
        'data/mail_template.xml',
        'view/emp_passport_register_view.xml',
        'view/emp_passport_request_view.xml',
        'view/int_passport_process_view.xml',
        'view/hr_view.xml',
        'cron.xml',
        'menu.xml',
    ],
    'demo': [
        'demo/passport_demo.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
