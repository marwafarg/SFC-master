# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'Biometric Device Integration for HR Attendance',
    'version': '1.0',
    'author': 'erp-bank',
    'website': 'http://www.erp-bank.com',
    'category': 'HR',
    'sequence': 15,
    'summary': 'Biometric Device Integration for HR Attendance.',
    'depends': ['hr_attendance'],
    'description': """
Biometric Device Integration for HR Attendance.
    """,
    'data': [
        'data/cron.xml',
        'security/ir.model.access.csv',
        'security/hr_security.xml',
        'views/hr_attendance_zkt_config_view.xml',
        'views/hr_view.xml',
        'views/res_company_view.xml',
        'wizard/add_employee_view.xml'
    ],
    'demo': [],
    'images': [],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
}
