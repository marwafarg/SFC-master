# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
from collections import defaultdict
from odoo.exceptions import UserError


class HrExpensePayment(models.Model):
    _name = 'hr.expense.payment'
    _description = "Expense"

    name = fields.Char(string="Name")

class YearYear(models.Model):
    _name = 'year.year'
    _description = "Year"

    name = fields.Char(string="Name")

class RecruitmentEmployeeSkill(models.Model):
    _name = 'hr.recruitment.employee.skill'
    _description = "Recruitment"

    name = fields.Char(string="Name")

class IssueWarning(models.Model):
    _name = "issue.warning"
    _description = "Issue"

    name = fields.Char(string="Name")

class WarningType(models.Model):
    _name = "warning.type"
    _description = "Warning"

    name = fields.Char(string="Name")

class ResDocumentType(models.Model):
    _name = 'res.document.type'
    _description = "Document"

    name = fields.Char(string="Name")

class EducationCertificate(models.Model):
    _name = 'education.certificate'
    _description = "Education"

    name = fields.Char(string="Name")

class NewJoiningEmployee(models.AbstractModel):
    _name = 'report.saudi_hr.report_new_joining_employee'
    _description = "Report"

    name = fields.Char(string="Name")

class Facility(models.Model):
    _name = "facility"
    _description = "Facility"

    name = fields.Char(string="Name")

class Villa(models.Model):
    _name = "villa"
    _description = "villa"

    name = fields.Char(string="Name")

class City(models.Model):
    _name = 'res.city'
    _description = "City"

    name = fields.Char(string="Name")

class AnnualTicket(models.Model):
    _name = 'annual.ticket'
    _description = "Ticket"

    name = fields.Char(string="Name")

class AnnualTicketEmployees(models.TransientModel):
    _name = 'annual.ticket.employees'
    _description = "Annual Ticket"

    name = fields.Char(string="Name")

class LeavesDetails(models.Model):
    _name = 'leaves.details'
    _description = "Leaves"

    name = fields.Char(string="Name")

class LeaveEncashmentDetails(models.TransientModel):
    _name = 'leave.encashment.details'
    _description = "Leaves Encashment"

    name = fields.Char(string="Name")

class EmployeeBonusLines(models.Model):
    _name = "employee.bonus.lines"
    _description = "Bonus"

    name = fields.Char(string="Name")

class EmployeeCard(models.Model):
    _name = 'hr.employee.card'
    _description = "Card"

    name = fields.Char(string="Name")

class CareerDevelopmentLines(models.Model):
    _name = 'hr.career.development.lines'
    _description = "Career"

    name = fields.Char(string="Name")

class ClearanceDepartment(models.Model):
    _name = 'clearance.department'
    _description = "Clearance"

    name = fields.Char(string="Name")

class TransferEmployee(models.Model):
    _name = 'transfer.employee'
    _description = "Transfer"

    name = fields.Char(string="Name")

class ProductLine(models.Model):
    _name = 'product.line'
    _description = "Product Line"

    name = fields.Char(string="Name")

class EmployeeDependent(models.Model):
    _name = 'employee.dependent'
    _description = "Employee Dependent"

    name = fields.Char(string="Name")

class EOSDetails(models.TransientModel):
    _name = 'eos.details'
    _description = "Eos"

    name = fields.Char(string="Name")

class ExpatsFee(models.Model):
    _name = 'expats.fee'
    _description = "Expats"

    name = fields.Char(string="Name")

class GroupMember(models.Model):
    _name = 'group.member'
    _description = "Group"

    name = fields.Char(string="Name")

class HadafPayslipLine(models.Model):
    _name = 'hadaf.payslip.line'
    _description = "Hadaf"

    name = fields.Char(string="Name")

class GrOperations(models.Model):
    _name = 'gr.operations'
    _description = "GR"

    name = fields.Char(string="Name")

class HrGrade(models.Model):
    _name = 'hr.grade'
    _description = "Grade"

    name = fields.Char(string="Name")

class HrGroupsConfiguration(models.Model):
    _name = "hr.groups.configuration"
    _description = "Groups Configuration"

    name = fields.Char(string="Name")

class EmployeeHealth(models.Model):
    _name = "emp.health.info"
    _description = "Health"

    name = fields.Char(string="Name")

class HrIqama(models.Model):
    _name = 'hr.iqama'
    _description = "Iqama"

    name = fields.Char(string="Name")

class MaintenanceEquipmentRequest(models.Model):
    _name = 'maintenance.equipment.request'
    _description = "Maintenance"

    name = fields.Char(string="Name")

class HRJobRequisition(models.Model):
    _name = 'hr.job.requisition'
    _description = "Requisition"

    name = fields.Char(string="Name")

class LeaveDetail(models.Model):
    _name = "leave.detail"
    _description = "Leave"

    name = fields.Char(string="Name")

class HREmployeeLeaving(models.Model):
    _name = "hr.employee.leaving"
    _description = "Leaving"

    name = fields.Char(string="Name")

class MultiReports(models.Model):
    _name = 'multi.reports'
    _description = "Reports"

    name = fields.Char(string="Name")

class HrLoan(models.Model):
    _name = 'hr.loan'
    _description = "Loan"

    name = fields.Char(string="Name")

class ManpowerPlan(models.Model):
    _name = "manpower.plan"
    _description = "Manpower"

    name = fields.Char(string="Name")

class InsuranceDetails(models.Model):
    _name = 'insurance.details'
    _description = "insurance"

    name = fields.Char(string="Name")

class AnalyticOvertime(models.Model):
    _name = 'analytic.overtime'
    _description = "Overtime"

    name = fields.Char(string="Name")

class EmployeePassportRegister(models.Model):
    _name = 'emp.passport.register'
    _description = "Passport"

    name = fields.Char(string="Name")

class HrPayslipExport(models.Model):
    _name = 'hr.payslip.export'
    _description = "Payslip"

    name = fields.Char(string="Name")

class EmployeeProbationReview(models.Model):
    _name = 'emp.probation.review'
    _description = "Probation"

    name = fields.Char(string="Name")

class HRSurveyFeedback(models.Model):
    _name = 'hr.survey.feedback'
    _description = "Survey"

    name = fields.Char(string="Name")

class HrSponsorshipTransfer(models.Model):
    _name = 'hr.sponsorship.transfer'
    _description = "Sponsorship"

    name = fields.Char(string="Name")

class HRVacation(models.Model):
    _name = 'hr.vacation'
    _description = "Vacation"

    name = fields.Char(string="Name")

class HrVisa(models.Model):
    _name = 'hr.visa'
    _description = "Visa"

    name = fields.Char(string="Name")

class HrEmployeeRecVisa(models.Model):
    _name = 'hr.employee.rec.visa'
    _description = "Employee Visa"

    name = fields.Char(string="Name")

class EmployeeAdvanceSalary(models.Model):
   _name = "hr.advance.salary"
   _description = "Salary"

   name = fields.Char(string="Name")

class AttendancePolicy(models.Model):
    _name = 'attendance.policy'
    _description = "Attendance"

    name = fields.Char(string="Name")

class HrAttendanceZktConfig(models.Model):
   _name = 'attendance.zkt.config'
   _description = "Attendance ZTK"

   name = fields.Char(string="Name")
