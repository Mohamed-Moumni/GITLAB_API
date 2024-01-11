from odoo import fields, models


class ProjectTags(models.Model):
    _name = "custom.project.tags"
    _description = "Custom Project Tags"

    name = fields.Char('Name', required=True)
    project_ids = fields.Many2many('project.project', 'project_custom_tags_rel', string='Projects')
    task_ids = fields.Many2many('project.task', 'task_custom_tags_rel', string='Tasks')
