from odoo import api, fields, models
from odoo.exceptions import ValidationError

class HostelRoom(models.Model):
    _name = "hostel.room"
    _description = "Model used to represent a room in an hostel."

    # Contraintes SQL
    """
Attention : si on ajoute une contrainte SQL alors qu'il existe déjà des enregistrements en base qui violent la contrainte,
alors la contrainte ne s'appliquera pas du tout et un message d'erreur apparaitra dans les logs.
    """

    _sql_constraints = [
        ('room_no_unique', 'UNIQUE(room_no)', "An hostel N° shoud be unique.")
    ]

    # Contraintes Python
    """
On indique dans le décorateur @api.constrains les champs qui sont impliqués dans la contraintes.
La contrainte est alors automatiquement revérifiée lorsque l'un des champs indiqués change.
    """

    @api.constrains('rent_amount')
    def _check_rent_amount_is_positive(self):
        """
        Contrainte Python pour vérifier que le montant du loyer est bien une valeur positive.
        """
        if self.rent_amount < 0:
            raise ValidationError("Error. The rent amount should be a positive value.")

    # ===============
    # Champs basiques
    # ===============

    name = fields.Char(string="Room Name")
    room_no = fields.Integer(string="Room No.")
    floor_no = fields.Integer(string="Floor No.")

    # =======================
    # Champs relatifs au prix
    # =======================

    # Pour définir un champ Monetary, il faut lui associer une devise (currency). On fait le lien ici avec le modèle des devises.
    currency_id = fields.Many2one(
        string="Currency",
        comodel_name='res.currency',
    )

    # Le paramètre 'currency_field' n'est pas obligatoire temps que notre champ devise se nomme 'currency_id'. Odoo est assez intelligent pour les associer.
    # Mais si on avais appeler 'currency_id' différemment, il aurait été obligatoire d'utiliser 'currency_field' pour indiquer la devise à laquelle rattacher le champ Monetary.
    rent_amount = fields.Monetary(
        string="Rent Amount",
        help="Enter rent amount per month",
        currency_field='currency_id',
    )

    # ===========================
    # Champs en lien avec l'hotel
    # ===========================

    """
    Une chambre ne peut avoir qu'un hotel (et un hotel plusieurs chambres) donc :

    room --> hostel (Many2one)
    hostel --> room (One2many)
    """

    hostel_id = fields.Many2one(
        string="Hostel",
        comodel_name='hostel.hostel',
        help="Name of the hostel",
    )

    # ==============================
    # Champs en lien avec l'étudiant
    # ==============================

    student_ids = fields.One2many(
        string="Students",
        comodel_name='hostel.student',
        inverse_name='room_id',
        help="Enter students"
    )

    # ===================================
    # Champs en lien avec les équipements
    # ===================================

    hostel_amenities_ids = fields.Many2many(
        comodel_name='hostel.amenities',       # le modèle lié
        relation="hostel_room_amenities_rel",  # le nom de la table qui stocke la relation en BDD
        column1="room_id",                     # le nom de la colonne qui stocke les enregistrements de ce modèle
        column2="amenity_id",                  # le nom de la colonne qui stocke les enregistrements du modèle lié
        string="Amenities",
        domain="[('active', '=', True)]",      # le domain qui permet de ne séléctionner que des aménagements actifs
        help="Select hostel room amenities",
    )
