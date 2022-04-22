# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'HR Transaction Report',
    'summary': """Generate Employee Transaction Report""",
    'version': '1.0',
    'description': """Generate Employee Transaction Report""",
    'author': 'erp-bank.',
    'website': 'http://www.erp-bank.com',
    'category': 'HR',
    'depends': ['saudi_hr_clearance',
        'saudi_hr_gr_operation_request', 'saudi_hr_vacations'],
    'license': 'OPL-1',
    'data': [
        'wizard/hr_transaction_report_view.xml',
        'menu.xml'
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
