# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'Attendance Sheet For Employee Attendance',
    'version' : '1.0',
    'author': 'erp-bank',
    'website': 'http://www.erp-bank.com',
    'category': 'HR',
    'sequence': 15,
    'summary': 'Attendance Sheet For Employee Attendance.',
    'depends': ['saudi_hr_overtime', 'saudi_hr_leaves_management', 'saudi_hr_payroll'],
    'description': """
Attendance Sheet For Employee Attendance.
    """,
    'data': [
        # 'data/payroll_data.xml',
        'security/ir.model.access.csv',
        'security/hr_security.xml',
        'wizard/generate_attendance_sheet_view.xml',
        'views/attendance_rules_view.xml',
        'views/attendance_policy_view.xml',
        'views/attendance_sheet_view.xml'
    ],
    'demo': [],
    'images': [],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
}
