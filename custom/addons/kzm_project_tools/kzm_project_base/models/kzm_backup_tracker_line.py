# -*- coding: utf-8 -*-

from odoo import fields, models, _
from datetime import datetime, timedelta, date
import os


class KzmBackupTrackerLine(models.Model):
    _inherit = 'kzm.backup.tracker.lines'
    data_base = fields.Many2one('project.database', string="Base de données")


class KzmBackupTracker(models.Model):
    _inherit = 'kzm.backup.tracker'

    def create_datas(self, blobs, kzm_backup_tracker_lines):
        successful = self.browse()
        for kbtl in kzm_backup_tracker_lines:
            list = []
            on_date = fields.Datetime.to_string(datetime.today().replace(hour=12))
            for blob in blobs:
                # from pprint import pprint
                # pprint(blob)
                on_date = fields.Datetime.to_string(blob.updated.replace(hour=12))
                name = os.path.basename(blob.name)
                start_date = fields.Datetime.to_string(blob.updated.replace(hour=3))
                end_date = fields.Datetime.to_string(blob.updated.replace(hour=21))
                if True:  # blob.content_type == 'application/zip':
                    # print(blob.updated.date())

                    if blob.updated.date() == datetime.today().date():
                        record = self.env['kzm.backup.tracker.gantt'].search(
                            [('start_date', '<=', on_date),
                             ('end_date', '>=', on_date),
                             ('gcloud_backup_line', '=', kbtl.id)])
                        # print("recc", record, line)
                        if len(record) > 0:
                            # print("in")
                            record.unlink()
                        values = {
                            'name': name,
                            'start_date': start_date,
                            'end_date': end_date,
                            'backup_name': kbtl.backup_name,
                            'backup_path': kbtl.backup_path,
                            'data_base': kbtl.data_base.id,
                            'days_to_keep': kbtl.days_to_keep,
                            'gcloud_backup_line': kbtl.id
                        }
                        list.append(values)
            count = len(list)
            for i in list:
                if count > 1:
                    i['color'] = 3
                    self.env['kzm.backup.tracker.gantt'].create(i)
                elif count == 1:
                    i['color'] = 10
                    self.env['kzm.backup.tracker.gantt'].create(i)
            i = {}
            if count == 0:
                i['color'] = 9
                i['start_date'] = fields.Datetime.to_string(datetime.today().replace(hour=3))
                i['end_date'] = fields.Datetime.to_string(datetime.today().replace(hour=21))
                i['name'] = "Not Found"
                i['backup_name'] = kbtl.backup_name
                i['backup_path'] = kbtl.backup_path
                i['days_to_keep'] = kbtl.days_to_keep
                i['gcloud_backup_line'] = kbtl.id
                i['data_base'] = kbtl.data_base.id
                record = self.env['kzm.backup.tracker.gantt'].search(
                    [('start_date', '<=', on_date),
                     ('end_date', '>=', on_date),
                     ('name', '=', "Not Found"),
                     ('gcloud_backup_line', '=', kbtl.id)])
                if len(record) > 0:
                    record.unlink()
                # pprint(i)
                self.env['kzm.backup.tracker.gantt'].create(i)
        successful.cleanup(kzm_backup_tracker_lines)

    # def create_datas(self, blobs, ids):
    #     successful = self.browse()
    #     for id in ids:
    #         list = []
    #         for blob in blobs:
    #             name = os.path.basename(blob.name)
    #             start_date = blob.updated
    #             end_date = blob.updated + timedelta(hours=24)
    #             if blob.content_type == 'application/octet-stream':
    #                 print(blob.updated.date())
    #                 if blob.updated.date() == datetime.today().date():
    #                     values = {
    #                         'name': name,
    #                         'start_date': start_date.date(),
    #                         'end_date': end_date.date(),
    #                         'bucket_name': id.backup_name,
    #                         'data_base': id.data_base.id,
    #                         'days_to_keep': id.days_to_keep
    #                     }
    #                     list.append(values)
    #         count = len(list)
    #         for i in list:
    #             if count > 1:
    #                 i['color'] = 3
    #                 self.env['kzm.backup.tracker.gantt'].create(i)
    #             elif count == 1:
    #                 i['color'] = 10
    #                 self.env['kzm.backup.tracker.gantt'].create(i)
    #         i = {}
    #         if count == 0:
    #             i['color'] = 9
    #             i['start_date'] = date.today()
    #             i['end_date'] = date.today() + timedelta(hours=24)
    #             i['name'] = "Not Found"
    #             i['bucket_name'] = id.backup_name
    #             i['data_base'] = id.data_base.id
    #             i['days_to_keep'] = id.days_to_keep
    #             self.env['kzm.backup.tracker.gantt'].create(i)
    #     successful.cleanup(ids)


class KzmBackupTrackerGantt(models.Model):
    _inherit = 'kzm.backup.tracker.gantt'
    data_base = fields.Many2one('project.database', string="Base de données")
