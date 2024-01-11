import json
import openai

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ChatgptRequest(models.Model):
    _name = 'chatgpt.request'
    _description = 'chatgpt.request'
    _rec_name = 'partner_id'

    partner_id = fields.Many2one('res.partner', string="Client")
    line_ids = fields.One2many('chatgpt.request.line', 'request_id', string="Client")
    total_tokens = fields.Integer(string="Total tokens", compute="_compute_total", store=True)
    total_amount = fields.Float(string="Total amount", compute="_compute_total", digits=(2, 6))

    @api.depends(
        'line_ids',
        'line_ids.total_tokens',
        'line_ids.amount',
    )
    def _compute_total(self):
        for record in self:
            record.total_tokens = sum(record.line_ids.mapped('total_tokens'))
            record.total_amount = sum(record.line_ids.mapped('amount'))

    def get_open_ai_response(self, prompt):

        api_key = self.env.company.openai_api_key
        model = self.env.company.openai_model
        custom_openai_model = self.env.company.custom_openai_model

        if not api_key or not (model or custom_openai_model):
            return False
        try:
            openai.api_key = api_key
            if custom_openai_model:
                response = openai.Completion.create(
                    model=custom_openai_model.fine_tuned_model,
                    prompt=prompt,
                    temperature=0
                )
                return response
            response = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system",
                     "content": "You answer customer questions and requests related to Odoo ERP."},
                    {"role": "user", "content": prompt},
                ],
            )
        except openai.error.AuthenticationError as e:
            raise ValidationError(str(e))
        return response

    def post_chatgpt_message(self, record, response):
        if self.env.company.custom_openai_model:
            content = response['choices'][0]['text']
        else:
            content = response.choices[0].message.content
        record.message_post(
            body=content,
            message_type='comment',
            subtype_xmlid='mail.mt_comment',
            author_id=self.env.ref('base.partner_root').id,
        )

    def save_to_chatgpt_request(self, response):
        if self.env.company.custom_openai_model:
            posted_response = response['choices'][0]['text']
        else:
            posted_response = response.choices[0].message.content
        vals = {
            'partner_id': self.env.user.partner_id.id,
            'response_json': json.dumps(response, indent=4, sort_keys=True),
            'request_uuid': response.get('id', ''),
            'model': response.get('model', ''),
            'posted_response': posted_response,
            'total_tokens': response.get('usage', {}).get('total_tokens', 0),
        }
        return self.env['chatgpt.request.line'].create(vals)

    def run_chatgpt(self, message):
        response = self.get_open_ai_response(message)
        line_id = False
        if response:
            line_id = self.save_to_chatgpt_request(response)
            line_id.write({
                'input_message': message,
            })
        return response, line_id
