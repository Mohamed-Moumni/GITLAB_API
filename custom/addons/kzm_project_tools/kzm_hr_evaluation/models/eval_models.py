# -*- coding: utf-8 -*-

from odoo import api,models,fields
from odoo.exceptions import ValidationError

class BaremeKzm(models.Model):
    _name = 'kzm.hr.bareme.eval'

    name = fields.Char(string='Name', required=True)
    note = fields.Float(string='Note', required=True)

class AxeEvaluation(models.Model):
    _name = 'kzm.hr.axe.eval'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=False)
    critere_eval_ids = fields.One2many('kzm.hr.critere.eval','hr_axe_id', string="Criteres")
    modele_eval_ids = fields.One2many('kzm.hr.modele.eval', 'hr_axe_id', string="Evaluation models")

class CritereEvaluation(models.Model):
    _name = 'kzm.hr.critere.eval'

    name = fields.Char(string='Designation', required=True)
    coef = fields.Float(string='Coef', required=False)
    description = fields.Text(string='Description', required=False)
    hr_axe_id = fields.Many2one('kzm.hr.axe.eval', string='Evaluation Axe', required=True)
    hr_bareme_ids = fields.Many2many('kzm.hr.bareme.eval','critere_eval_bareme_rel', 'hr_modele_id', 'hr_bareme_id', string='Baremes')

class ModeleEvaluation(models.Model):
    _name = 'kzm.hr.modele.eval'

    name = fields.Char(string='Designation', required=True)
    hr_axe_id = fields.Many2one('kzm.hr.axe.eval', string='Axe Evaluation', required=True)
    hr_critere_ids = fields.Many2many('kzm.hr.critere.eval', 'modele_eval_critere_rel', 'hr_modele_id', 'hr_critere_id', 'Criteres')

class KzmEvaluation(models.Model):
    _name = 'kzm.hr.evaluation.eval'

    name = fields.Char(string='Designation', required=True)
    date_eval = fields.Date(string='Date', required= True)
    employe_id = fields.Many2one('hr.employee', string='Salary', required=True)
    hr_modele_id = fields.Many2one('kzm.hr.modele.eval', string='Evaluation Model', required=True)
    mean_note = fields.Float('Mean note', compute='_compute_mean_note')# compute
    hr_axe_id = fields.Many2one('kzm.hr.axe.eval', related='hr_modele_id.hr_axe_id',string='Axe Evaluation')
    hr_evaluation_line_ids = fields.One2many('kzm.hr.evaluation.line.eval',
                                    'hr_evaluation_id',
                                     'Evaluation lines')# On change

    @api.depends('hr_evaluation_line_ids')
    def _compute_mean_note(self):
        for o in self:
            notes = sum([l.computed_note for l in o.hr_evaluation_line_ids])
            coefs = sum([l.coef for l in o.hr_evaluation_line_ids])
            o.mean_note = float(notes) / (coefs or 1.0)

    @api.onchange('hr_modele_id')
    def on_change_model(self):
        for o in self:
            if o.hr_evaluation_line_ids:
                o.hr_evaluation_line_ids.unlink()
            if o.hr_axe_id:
                criteres = self.env['kzm.hr.critere.eval'].search([('hr_axe_id','=', o.hr_axe_id.id)])
                for crt in criteres:
                    eval_line = self.env['kzm.hr.evaluation.line.eval'].new({
                        'name': crt.id,
                        'coef': crt.coef,
                        'hr_evaluation_id': o.id,
                    })
                    eval_line.hr_evaluation_id = o


class KzmEvaluationLine(models.Model):
    _name = 'kzm.hr.evaluation.line.eval'

    name = fields.Many2one('kzm.hr.critere.eval', string='Name', required=True)
    note = fields.Many2one('kzm.hr.bareme.eval', string='Note', required=False)
    coef = fields.Float(string='Coef', related='name.coef')
    computed_note = fields.Float('Note * Coef', compute = '_compute_note')# compute
    commentaire = fields.Text("Commentaire")
    hr_evaluation_id = fields.Many2one('kzm.hr.evaluation.eval', string='Evaluation', required=True, ondelete='cascade')

    @api.multi
    def _compute_note(self):
        for o in self:
            o.computed_note = o.note.note * o.coef

class KzmEvaluationPlan(models.Model):
    _name = 'kzm.hr.plan.evaluation.eval'

    name = fields.Char('Name', compute='_compute_name')
    employe_id = fields.Many2one('hr.employee', string='Salary', required=True)
    date_plan = fields.Date(string='Date', required= True)
    date_start = fields.Date(string='Date start', required=True)
    date_end = fields.Date(string='Date end', required=True)
    note = fields.Float(string='Note', required = True, compute='_compute_note')
    classe = fields.Char(string='Classification')
    period_str = fields.Char(string='Period', compute='_compute_period_str')

    hr_evaluation_plan_line_ids = fields.One2many('kzm.hr.plan.evaluation.line.eval',
                                             'hr_plan_evaluation_id',

                                             'Evaluation Plan lines')
    @api.multi
    def _compute_name(self):
        for o in self:
            o.name = str(o.employe_id and o.employe_id.name or '') +\
                     ' : ' + str(o.date_start or '')+' - '+ str(o.date_end or '')

    @api.multi
    @api.depends('hr_evaluation_plan_line_ids')
    def _compute_note(self):
        for o in self:
            notes = sum([l.computed_note for l in o.hr_evaluation_plan_line_ids])
            coefs = sum([l.coef for l in o.hr_evaluation_plan_line_ids])
            o.note = float(notes) / (coefs or 1)

    @api.multi
    def _compute_period_str(self):
        for o in self:
            o.period_str = str(o.date_start or '') + ' - ' + str(o.date_end or '')

    @api.constrains('date_start','date_end')
    def check_dates_period(self):
        for o in self:
            if o.date_start and o.date_end:
                if o.date_start > o.date_end:
                    raise ValidationError("Date start must be less than date end")

    @api.onchange('date_start','date_end')
    def on_change_period(self):
        def group_by_axe(objects):
            results = {}
            for obj in objects:
                if obj.hr_axe_id:
                    if obj.hr_axe_id.id in results:
                        results[obj.hr_axe_id.id].append(obj)
                    else:
                        results[obj.hr_axe_id.id] = [obj, ]
            return results
        for o in self:
            if not(o.employe_id and o.date_start and o.date_end):
                continue
            evals = self.env['kzm.hr.evaluation.eval'].search([
                ('employe_id', '=', o.employe_id.id),
                ('date_eval', '<=', o.date_end),
                ('date_eval', '>=', o.date_start)])
            grouped_evals = group_by_axe(evals)
            for axe_id, evs in grouped_evals.items():
                mean_note = sum([e.mean_note for e in evs]) / (len(evs) or 1.0)
                for line in o.hr_evaluation_plan_line_ids:
                    if line.name and line.name.id == axe_id:
                        #line.update({'note': mean_note, })
                        line.note = mean_note
                        break
                else:
                    plan_line = self.env['kzm.hr.plan.evaluation.line.eval'].new({
                        'name': axe_id,
                        'note': mean_note,
                        'coef': 1.0,
                        'hr_plan_evaluation_id': o.id,
                    })
                    plan_line.hr_plan_evaluation_id = o

class KzmEvaluationPlanLine(models.Model):
    _name = 'kzm.hr.plan.evaluation.line.eval'

    name = fields.Many2one('kzm.hr.axe.eval', string='Axe Eval', required=True)
    note = fields.Float(string='Note', required = True)
    coef = fields.Float(string='Coef', related=False)
    computed_note = fields.Float('Note * Coef', compute='_compute_note')  # compute
    hr_plan_evaluation_id = fields.Many2one('kzm.hr.plan.evaluation.eval', string='Evaluation Plan', required=True, ondelete='cascade')

    @api.multi
    def _compute_note(self):
        for o in self:
            o.computed_note = o.note * o.coef

    _sql_constraints = [
        ('axe_plan_unique', 'unique(name,hr_plan_evaluation_id)',
         "Another plan line already exists in this plan with the same (axe, plan)!"),
    ]