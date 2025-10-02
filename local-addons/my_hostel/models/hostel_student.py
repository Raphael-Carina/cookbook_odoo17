from odoo import fields, models

class HostelStudent(models.Model):
    _name = 'hostel.student'
    _description = "Model used to represent students which locate rooms in hostels."

    # ===============
    # Champs basiques
    # ===============

    student_firstname = fields.Char(string="Firstname")
    student_lastname = fields.Char(string="Lastname")
    gender = fields.Selection(
        selection=[('male','Male'),('female','Female'),('other','Other')],
        string="Gender"
    )
