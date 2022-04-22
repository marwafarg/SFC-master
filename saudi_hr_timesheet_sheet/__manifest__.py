# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': "Saudi HR Timesheet Sheet",
    'summary': "Saudi HR Timesheet Sheet",
    'description': """
        Saudi HR Timesheet Sheet
    """,
    'author': 'erp-bank.',
    'website': 'http://www.erp-bank.com',
    'category': 'HR',
    'version': '1.0',
    'license': 'OPL-1',
    'depends': [
        'hr_timesheet_sheet',
        'saudi_hr_overtime',
        'hr_payroll',
        # 'sync_hr_payroll',
        'saudi_hr_leaves_management'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/hr_payroll_data.xml',
        'views/hr_timesheet_sheet.xml',
        'views/hr_payroll_view.xml',
    ],
    'demo': [],
    'images': [
        'static/description/main_screen.jpg'
    ],
    "price": 30.0,
    "currency": "EUR",
    'installable': True,
    'auto_install': False,
}
