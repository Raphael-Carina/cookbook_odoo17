from odoo import api, fields, models
from datetime import timedelta

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
        comodel_name='hostel.room',
        help="Select hostel room",
    )

    # ==============================================
    # Champs relatifs à l'hostel (ex. champ related)
    # ==============================================

    """
Les utilisateurs Odoo ne peuvent avoir accèsqu'aux champs qui appartiennent au modèle sur lequel ils se trouvent.
Pour pouvoir avoir accès à des champs d'autres modèle, on peut utiliser les champs related.
Il s'agit d'un type de champ particulier qui réfère à un autre champ d'un modèle différent.
Pour créer un champ related, on doit spécifier l'argument 'related' au champ et donner le chemin vers le champ à afficher.
Dans cet exemple, hostel_id est un champ related qui permet d'afficher sur le modèle hostel.student l'hostel de la room du student.

--> les champs related sont en réalité des champs computes.

Note :

Attention aux N queries !
Il est préférable de ne pas utiliser de champ related dans les méthodes create() ou write().

Exemple avec les modèles sale.order et sale.order.line :


-------

class SaleOrder(models.Model):
    _name = 'sale.order'
    
    partner_id = fields.Many2one('res.partner')
    partner_name = fields.Char(related='partner_id.name')
    order_line = fields.One2many('sale.order.line', 'order_id')

----

class SaleOrderLine(models.Model):
    _name = 'sale.order.line'
    
    order_id = fields.Many2one('sale.order')
    
    # Champ related qui "remonte" vers sale.order
    partner_id = fields.Many2one(related='order_id.partner_id', store=True)


    @api.model
    def create(self, vals):
        line = super().create(vals)
        
        # ⚠️ PROBLÈME : Utilisation du champ related
        if line.partner_id:  # Accès au champ related
            # Faire quelque chose avec partner_id
            self._do_something(line.partner_id)
        
        return line
-------

Le problème a lieu car Odoo optimise en retardant le calcul des champs related.
Dons au moment de notre if line.partner_id, ce champ n'est pas encore calculé, donc il va faire une requête SQL.

Si on créer 100 sale.order.line d'un coup, cela représente 100 requêtes SQL.

Le mieux dans ces cas là c'est de passer directement par le champ du modèle parent : if line.order_id.partner_id !
    """

    hostel_id = fields.Many2one(
        string="Hostel",
        comodel_name='hostel.hostel',
        related='room_id.hostel_id',
    )

    # ========================================================================================
    # Champs relatifs à la date d'entrée/sorte et durée (ex. champ compute avec readony=False)
    # ========================================================================================

    admission_date = fields.Date(
        string="Admission Date",
        default=fields.Datetime.today,
    )

    discharge_date = fields.Date(
        string="Discharge date",
        help="Date on which student discharge",
    )

    duration = fields.Integer(
        string="Duration",
        compute="_compute_check_duration",
        inverse="_inverse_duration",
        help="Enter duration of living",
    )


    # =================
    # Méthodes computes
    # =================

    """
Le champ 'duration' est un champ compute mais qui possède une méthode inverse.
Cela le rends automatiquement readonly=False (alors que les champs compute sont normalement readonly).

Une méthode compute assigne une valeur au champ tandis qu'une méthode inverse assigne une valeur aux dépendances.

Attention : 
Une méthode compute est déclenchée dès lors que l'une de ses dépendances change tandis qu'une méthode inverse ne se déclenche qu'à l'enregistrement.

Les champs computes ne sont pas stockés en base de donnée, ils sont calculés "à la volée". C'est à cause de cela que l'on ne peut pas utiliser de write
ou de search sur ces champs (ni les utiliser dans les vues search).
L'ORM Odoo utilise un système de cache pour ne pas avoir a recalculer inutilement les champs compute. Il utilise le décorateur @api.depends() pour voir
lorsqu'il a besoin d'invalider son cache et de relancer le calcul du champ compute.

Dans une méthode compute, il faut bien s'assurer que la méthode donne une valeur au champ dans tous les cas!


OBSERVATION IMPORTANTE sur les NewId :

Lorsqu'on modifie un champ dans l'interface Odoo, la méthode compute peut être 
appelée PLUSIEURS fois (souvent 4 fois) :
- 2 fois sur l'enregistrement RÉEL : hostel.student(1,)
- 2 fois sur un enregistrement VIRTUEL : hostel.student(<NewId origin=1>,)

Le NewId est une copie temporaire créée par Odoo pour gérer l'état "non sauvegardé"
du formulaire. Cela permet d'annuler les modifications sans toucher à la base de données.

C'est un comportement NORMAL et attendu. Les méthodes compute doivent donc être :
- Idempotentes (résultat identique peu importe le nombre d'appels)
- Rapides (pas de calculs lourds)
- Sans effets de bord (pas de write/create)


-----------------------------------------------------------------------------------------------------------------------------

Points pas clairs du tout :

1) Déclenchement des _compute et des _inverse

Lorsque je modifie discharge_date, cela provoque immédiatemment _compute_check_duration() pour mettre à jour 'duration'.
Ensuite, lorsque j'enregistre, la méthode _inverse_duration() est appelée car 'duration' à changé.
Mais discharge_date est déjà correcte donc rien ne se passe et discharge_date ne change pas.

Maintenant, dans le cas où je modifie directement duration, cela appelle _inverse_duration lors de l'enregistrement et ça met discharge_date à jour.
Là je ne comprends pas pourquoi la modification de discharge_date n'appelle pas le méthode _compute_check_duration() ???


2) Appels multiples dans les méthodes

Lorsque je change discharge_date, je vois qu'on passe en réalité 4 fois dans la méthode _compute_check_duration().
2 fois avec un self = hostel.student(x,)
2 fois avec un self = hostel.student(<NewId origin=x>,)

J'ai bien compris qu'Odoo travaille avec des copies temporaires des enregistrements pour pouvoir facilement revenir en arrière mais bon, le fonctionnement
reste tout de même bien mystérieux.
    """

    @api.depends('admission_date', 'discharge_date')
    def _compute_check_duration(self):
        """
        Méthode qui donne une valeur au champ 'duration'.
        Se déclenche lorsque l'on change la valeur de admission_date ou discharge_date.
        'duration' corresponds au nombre de jour entre 'admission_date' et 'discharge_date'.


        Note :
        Lorsqu'Odoo déclenche une méthode compute, il fait les opérations suivante :
        - invalide le champ compute dans son cache
        - refixe la valeur du champ sur sa valeur par défaut, c'est à dire 0 pour les champ Int, Float, sinon False, ou ''.
        - exécute la méthode compute
        - remet la nouvelle valeur du champ dans son cache

        Donc concrètement, sur l'interface utilisateur Odoo, si j'ai duration=15 et que je change la valeur de 'discharge_date' pour rajouter un jour,
        duration vaudra 16. Mais au début du traitement, dans le debug si je fais self.duration ou record.duration, j'aurais 0 (et pas 15)!
        Ce comportement permet de faire en sorte que même lorsque la méthode compute n'assigne pas correctement sa valeur à un champ compute (if qui ne 
        se déclenche pas), le champ prenne sa valeur par défaut (0) plutôt qu'une ancienne valeur "périmée".
        """
        for record in self:
            if record.admission_date and record.discharge_date:
                record.duration = (record.discharge_date - record.admission_date).days

    def _inverse_duration(self):
        """
        Méthode qui donne une valeur à jour au champ 'discharge_date' lorsque le champ 'duration' change.
        Cette méthode est donc appelée à chaque fois que 'duration' change puis que l'on enregistre, ce qui arrive notamment quand :
        - on modifie 'duration' directement depuis l'interface
        - lorsque l'on modifie 'admission_date' ou 'discharge_date', ce qui active _compute_check_duration et met 'duration' à jour --> du coup duration change et appel donc cette méthode.
        """
        for record in self:

            # Cas où il y a à la fois une date d'admission ET une date de départ
            if record.discharge_date and record.admission_date:

                # On calcule alors le nombre de jours qui séparent la date d'admission et la date de départ
                duration = (record.discharge_date - record.admission_date).days

                # Si cet écart ne corresponds pas à la valeur du champ 'duration' (record.duration), alors on met à jour la date de départ. (elle vaut la date d'admission + la vraie duration (record.duration)).
                if duration != record.duration:
                    record.discharge_date = (record.admission_date + timedelta(days=record.duration)).strftime('%Y-%m-%d')

            # Dans le cas où l'on met une durée et qu'il y a une date d'admission mais pas de date de départ, on vient mettre la date de départ à jour selon la même logique.
            elif record.admission_date and not record.discharge_date:
                record.discharge_date = (record.admission_date + timedelta(days=record.duration)).strftime('%Y-%m-%d')

