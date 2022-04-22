# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "Attendance Report",
    'summary': """New Module For Employee Attendance Report""",
    'description': """
        Create new Module for Employee Attendance Report
    """,
    'author': 'erp-bank.',
    'website': 'http://www.erp-bank.com',
    'license': 'OPL-1',
    'category': 'HR',
    'version': '1.0',
    'depends': ['hr_attendance'],
    'data': [
        'wizard/employee_attendance_report_wizard.xml',
        'views/menu.xml',
        'report/employee_attendance_report.xml',
    ],
    'installable': True,
    'application': False,
}
