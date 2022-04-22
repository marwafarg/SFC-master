# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

import base64
from odoo import api, fields, models, _
import io
import xlwt
from odoo.exceptions import Warning


class AnnualTicketReport(models.TransientModel):
    _name = 'annual.ticket.report'
    _description = "Annual Ticket Report"

    filename = fields.Char(string='File Name', size=64)
    excel_file = fields.Binary(string='Excel File')

    def generate_annual_ticket_excel_report(self):
        try:
            format0 = xlwt.easyxf('font:height 230, bold True; pattern: pattern solid, fore-colour gray25; align:vert center, horiz center; borders: top_color black, bottom_color black, right_color black, left_color black,\
                left thin, right thin, top thin, bottom thin;')
            format1 = xlwt.easyxf('font:height 230, bold True; pattern: pattern solid, fore_colour gray25; align:vert center, horiz left;borders: top_color black, bottom_color black, right_color black, left_color black,\
                left thin, right thin, top thin, bottom thin;')
            format2 = xlwt.easyxf('font:height 230, bold False; pattern: pattern solid, fore_colour white; align:vert center, horiz left;borders: top_color black, bottom_color black, right_color black, left_color black,\
                left thin, right thin, top thin, bottom thin;')
            workbook = xlwt.Workbook()
            ticket_ids = self.env['annual.ticket'].browse(self._context.get('active_ids') or 0)
            for ticket in ticket_ids:
                if ticket.year_id.name == '/':
                    sheet = workbook.add_sheet(ticket.ref or '/')
                else:
                    sheet = workbook.add_sheet(ticket.name + '-' + ticket.year_id.name)
                sheet.write_merge(0, 0, 0, 7, 'Company Name : ' + self.env.user.company_id.name, format0)
                sheet.write_merge(1, 1, 0, 7, 'Year : ' + ticket.year_id.name, format0)
                row = 3
                column = 0
                sheet.col(0).width = 256 * 15
                sheet.write(row, column, 'Employee', format1)
                sheet.col(1).width = 256 * 15
                sheet.write(row , column + 1, 'Dependent(s)', format1)
                sheet.col(2).width = 256 * 20
                sheet.write(3, column + 2, 'Allocated Ticket(s)', format1)
                sheet.col(3).width = 256 * 20
                sheet.write(3, column + 3, 'Used Ticket(s)', format1)
                sheet.col(4).width = 256 * 20
                sheet.write(3, column + 4, 'Allocated Amount', format1)
                sheet.col(5).width = 256 * 15
                sheet.write(3, column + 5, 'Used Amount', format1)
                sheet.col(6).width = 256 * 20
                sheet.write(3, column + 6, 'Remaining Amount', format1)
                sheet.col(7).width = 256 * 20
                sheet.write(3, column + 7, 'Allowance Amount', format1)
                row += 1
                allocated_tickets = total_used_tickets = allocated_amount = used_amount = remaining_amount = total_allowance = 0
                for line in ticket.annual_ticket_detail_ids:
                    dependents = line.adults + line.infant + line.children
                    allowance = sum(line.other_hr_payslip_ids.mapped('amount'))
                    used_tickets = len(line.ticket_status_ids)
                    allocated_tickets += dependents
                    total_used_tickets += used_tickets
                    allocated_amount += line.allocated_amount
                    used_amount += line.used_amount
                    remaining_amount += line.remaining_amount
                    total_allowance += allowance
                    sheet.write(row, column, line.employee_id.name or '', format2)
                    sheet.write(row, column+1, dependents or '0', format2)
                    sheet.write(row, column+2, dependents or '0', format2)
                    sheet.write(row, column+3, used_tickets or '0', format2)
                    sheet.write(row, column+4, line.allocated_amount or '0.00', format2)
                    sheet.write(row, column+5, line.used_amount or '0.00', format2)
                    sheet.write(row, column+6, line.remaining_amount or '0.00', format2)
                    sheet.write(row, column+7, allowance or '0.00', format2)
                    row += 1
                row += 1
                sheet.write(row + 2, column, 'Total', format1)
                sheet.write(row + 2, column + 1, '', format1)
                sheet.write(row + 2, column + 2, allocated_tickets or '0', format1)
                sheet.write(row + 2, column + 3, total_used_tickets or '0', format1)
                sheet.write(row + 2, column + 4, allocated_amount or '0.00', format1)
                sheet.write(row + 2, column + 5, used_amount or '0.00', format1)
                sheet.write(row + 2, column + 6, remaining_amount or '0.00', format1)
                sheet.write(row + 2, column + 7, total_allowance or '0.00', format1)

            filename = ("Annual Ticket Report.xls")
            fp = io.BytesIO()
            workbook.save(fp)
            fp.seek(0)
            data_of_file = fp.read()
            fp.close()
            out = base64.encodestring(data_of_file)
            self.write({'excel_file': out, 'filename': filename})
            return self.return_wiz_action(self.id)

        except Exception as e:
            raise Warning(_('You are not able to print this report please contact your '
                            'administrator : %s ' % str(e)))

    def return_wiz_action(self, res_id, context=None):
        """
            Return Admin Reports
        """
        return {
            'name': 'Annual Ticket Report',
            'view_mode': 'form',
            'res_id': res_id,
            'res_model': 'annual.ticket.report',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'context': context,
            'target': 'new',
        }
