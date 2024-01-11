from odoo import api, fields, models


class ChatgptTrainingData(models.Model):
    _name = 'chatgpt.training.data'
    _description = 'chatgpt.training.data'

    model_id = fields.Many2one('chatgpt.model')
    prompt = fields.Text(string="Prompt", required=True)
    completion = fields.Text(string="Completion", required=True)
