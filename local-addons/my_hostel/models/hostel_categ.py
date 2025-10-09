from odoo import api, fields, models
from odoo.exceptions import ValidationError

class HostelCateg(models.Model):
    _name = 'hostel.category'
    _description = "Model used to create hostel categories."


    """
Le but de ce modèle est de créer un modèle avec une hiérarchie dans les instances.
Cela signifie que chaque enregistrement pourra avoir un autre enregistrement comme parent et plusieurs enregistrements comme enfant.
Pour cela, on fait :

- un champ Many2one qui référence le parent.
- un champ One2many qui référence les enfants.

-----------------------------------------------------------------
Sur le champ 'parent_id', on met ondelete='restrict'.
Cela permet d'empêcher la suppression d'un enregistrement s'il est utilisé comme parent par un autre enregistrement.
Conctrètement, si j'essaie de supprimer un tel enregistrement, j'aurais un message d'erreur avec le texte :

```
The operation cannot be completed: another model requires the record being deleted. If possible, archive it instead.

Model: Model used to create hostel categories. (hostel.category)
Constraint: hostel_category_parent_id_fkey
```

En effet, dès que l'on créer un champ Many2one dans Odoo, il crée automatiquement un contrainte de clé étrangère comme : hostel_category_parent_id_fkey dont le but
est de s'assurer que l'enregistrement vers lequel il pointe existe. C'est ensuite 'ondelete' qui indique à la clé comment réagir.
-----------------------------------------------------------------

L'utilisation de _parent_store = True .

_parent_store est un champ natif Odoo qui permet de "simplifier" le travail avec les modèles hiérarchiques.
Il permet la création du champ parent_path, qui gère la hiérarchie des enregistrements. C'est en quelque sorte le fil d'ariane d'un enregistrement qui remonte
son arbre généalogique. Il est calculé automatiquement et est composé des ID des enregistrements parents.

Ex : 
1/2/3/5 --> signifie que le parent direct de mon enregistrement actuel est celui d'ID 5, qui est lui même l'enfant de celui d'ID 3 etc.
Cela signifie que l'arbre ressemble à quelque chose comme :

        1
       / \
      /   \
     ?     2
          / \
         /   \
        ?     3
             / \
            /   \
           ?     5
                / \
               /   \
              ?    enreg. actuel

En utilisant _parent_store = True, on rends les requêtes de recherches plus rapides (les recherches utilisant child_of), mais
on rends les opérations d'écritures/modifications (write) un peu plus lente car l'arbre doit être modifié aussi.
-----------------------------------------------------------------

Concrètement, cette structure de modèle hiérarchique avec _parent_store = True est très efficace pour un modèle où nos catégories changent peu et 
où l'on fait beaucoup de recherches dessus. 

Par contre, elle ne convient pas très bien dans un contexte où l'on ferait souvent des modifications sur les catégories.
    """

    # ==============
    # Champs de base
    # ==============

    name = fields.Char(string="Category")

    # ====================
    # Champs de hiérarchie
    # ====================

    _parent_store = True
    _parent_name = "parent_id"


    parent_id = fields.Many2one(
        string="Parent Category",
        comodel_name="hostel.category",
        ondelete="restrict",
        index=True,
    )

    # Ce champ serait créer automatiquement par l'utilisation de _parent_store (cf: texte explicatif au début du fichier du modèle).
    parent_path = fields.Char(
        string="Parent path",
        index=True,
        unaccent=False,
    )

    child_ids = fields.One2many(
        string="Child Categories",
        comodel_name="hostel.category",
        inverse_name="parent_id",
    )

    @api.constrains('parent_id')
    def _check_hierarchy(self):
        """
        J'ai bien l'impression que cette méthode est inutile.
        Je comprends que le but est de faire en sorte qu'un enregistrement ne puisse pas être à la fois parent ET enfant d'un autre enregistrement.
        Par exemple, si j'ai un enregistrement N qui a un enfant N1, alors je ne peux pas modifier N pour lui mettre N1 comme parent.

        La logique de la méthode est bonne mais il y a déjà une méthode : _parent_store_update (odoo/odoo/models.py) qui semble détecter les problèmes de récursions.

        Peut être que la méthode reste utile dans un autre contexte ?

        """
        if not self._check_recursion():
            raise models.ValidationError('Error. You cannot create recursive categories.')
