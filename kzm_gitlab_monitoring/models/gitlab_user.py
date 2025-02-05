from odoo import models,fields

class GitlabUser(models.Model):
    """
        GitlabUser model for gitlab member

    Args:
        models (models.Model): Odoo ORM Model
    """
    
    _name = "gitlab.user"
    _description = "Gitlab User"
    
    name = fields.Char("name")
    username = fields.Char('Username')
    gitlab_id = fields.Char('gitlab_id')
    avatar = fields.Char('avatar')