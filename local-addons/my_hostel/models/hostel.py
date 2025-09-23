from odoo import fields, models

class Hostel(models.Model):
    _name = 'hostel.hostel'
    _description = "Information about hostel"

    # ==============
    # Champs simples
    # ==============

    name = fields.Char(string="Hostel Name", required=True)
    hostel_code = fields.Char(string="Code", required=True)
    street = fields.Char(string="Street")
    street2 = fields.Char(string="Street 2")

    # ===================
    # Champs relationnels
    # ===================

    state_id = fields.Many2one(string="State", comodel_name="res.country.state")
