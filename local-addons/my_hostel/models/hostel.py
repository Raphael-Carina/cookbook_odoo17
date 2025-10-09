from odoo import api, fields, models

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
    zip = fields.Char(string="Zip", change_default=True)
    city = fields.Char(string="City")
    phone = fields.Char(string="Phone", required=True)
    mobile = fields.Char(string="Mobile", required=True)
    email = fields.Char(string="Email")
    hostel_floors = fields.Integer(string="Total Floors")
    image = fields.Binary(string="Hostel Image")
    active = fields.Boolean(string="Active", default=True, help="Activate/Deactivate hosteel record")
    type = fields.Selection(selection=[("male", "Boys"), ("female", "Girls"), ("common", "Common")], help="Type of Hostel", required=True, default="common")
    other_info = fields.Text(string="Other Information", help="Enter more information")
    description = fields.Html(string="Description")
    hostel_rating = fields.Float(string="Hostel Average Rating",
                                # digits=(3, 1),
                                digits='Rating Value'
                                )

    # ===================
    # Champs relationnels
    # ===================

    state_id = fields.Many2one(string="State", comodel_name="res.country.state")
    country_id = fields.Many2one(string="Country", comodel_name="res.country")
    category_id = fields.Many2one(string="Category", comodel_name="hostel.category")

    # =========
    # Overrides
    # =========

    @api.depends('name', 'hostel_code')
    def _compute_display_name(self):
        """
        Override de la méthode pour modifier le champ 'display_name' du modèle.
        """
        for record in self:
            if record.name:
                name = record.name
                if record.hostel_code:
                    name = f'{name} ({record.hostel_code})'

                record.display_name = name
            
            # Si l'on ne gère pas le cas où name n'existe pas, on aura une erreur en essayant de créer une nouvelle instance puisque la méthode ne pourra pas assigner de display_name à l'instance
            else:
                record.display_name = False

# test
