import base64
import json
import logging
import openai

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class ChatgptModel(models.Model):
    _name = 'chatgpt.model'
    _description = 'chatgpt.model'

    name = fields.Char(string="Nom", required=True)
    fine_tuned_model = fields.Char(string="Fine tuned model", copy=False)
    job_id = fields.Char(string="Job ID", copy=False)
    training_file = fields.Binary(string="File", copy=False)
    training_file_name = fields.Char(string="Filename", copy=False)
    training_data_ids = fields.One2many('chatgpt.training.data', 'model_id', copy=True)
    base_model = fields.Selection([
        ('ada', 'ada'),
        ('babbage', 'babbage'),
        ('curie', 'curie'),
        ('davinci', 'davinci'),
    ], string='Base Model', required=True)
    state = fields.Selection([
        ('new', 'New'),
        ('pending', 'Pending'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
    ], string='Status', default='new')

    def generate_jsonl_file(self):
        prompt_suffix = "->"
        completion_suffix = "\n"
        training_data = []
        for line_id in self.training_data_ids:
            line = {
                "prompt": line_id.prompt + prompt_suffix,
                "completion": line_id.completion + completion_suffix,
            }
            training_data.append(line)

        file_data = '\n'.join([json.dumps(line) for line in training_data])
        self.training_file = base64.encodebytes(file_data.encode('utf-8'))
        self.training_file_name = self.name + '_training.jsonl'
        url = '/web/content/chatgpt.model/%s/training_file/%s?download=true' % (self.id, self.training_file_name)
        return {
            'name': 'Download File',
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
            'params': {
                'popup': 'true',
                'norefresh': 'true'
            },
            'context': {
                'message': 'Redirecting to download link...'
            },
            'js_code': "window.open('%s', '_blank');" % url
        }

    def create_fine_tuning_job(self):
        openai.api_key = self.env.company.openai_api_key

        upload_response = openai.File.create(
            file=base64.b64decode(self.training_file),
            purpose='fine-tune'
        )
        file_id = upload_response.id

        fine_tuning_job = openai.FineTune.create(
            model=self.base_model,
            training_file=file_id,
        )
        _logger.info("Openai create_fine_tuning_job %s" % (fine_tuning_job))
        self.job_id = fine_tuning_job["id"]

    def get_fine_tuning_state(self):
        openai.api_key = self.env.company.openai_api_key
        response = openai.FineTune.list()
        _logger.info("Openai get_fine_tuning_state %s" % response)
        job = next((job for job in response["data"] if job["id"] == self.job_id), None)
        self.state = job["status"]
        self.fine_tuned_model = job["fine_tuned_model"]

    def open_training_data_action(self):
        return {
            'name': _('Training data'),
            'domain': [('id', 'in', self.training_data_ids.ids)],
            'res_model': 'chatgpt.training.data',
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
            'context': {
                'default_model_id': self.id,
            }
        }
