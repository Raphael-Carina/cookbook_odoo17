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

    # ============================
    # Champs relatifs à la chambre
    # ============================

    """
    Un étudiant ne peut avoir qu'une chambre (et une chambre peut théoriquement avoir plusieurs étudiant) donc :

    hostel.student --> hostel.room : Many2one
    hostel.room --> hostel.student : One2many

    Concrètement :
    Sur un étudiant on peut voit la chambre qu'il occupe.
    Sur un chambre on peut voir la liste de ses occupants.
    """

    room_id = fields.Many2one(
        string="Room",
        comodel_name='hostel.room'
    )
