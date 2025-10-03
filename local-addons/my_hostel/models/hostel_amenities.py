from odoo import fields, models

class HostelAmenities(models.Model):
    _name = 'hostel.amenities'
    _description = "Model used to describe the hostel amenities"

    name = fields.Char(string="Name", help="Provided Hostel Amenity")
    active = fields.Boolean(string="Active", help="Activate/Deactivate whether the amenity should be given or not")
