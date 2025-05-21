import pandas as pd
import xlrd
from django.core.management.base import BaseCommand
from quiz.models import Question
from django.db.utils import IntegrityError


class Command(BaseCommand):
    help = '从 XLS 文件导入题目数据到数据库'

    def add_arguments(self, parser):
        parser.add_argument('xls_path', type=str, help='XLS 文件路径')

    def handle(self, *args, **kwargs):
        xls_path = kwargs['xls_path']
        wb = xlrd.open_workbook(xls_path)
        sheet = wb.sheet_by_index(0)

        for row in range(1, sheet.nrows):
            number = int(sheet.cell_value(row, 0))
            type = sheet.cell_value(row, 1)
            content = sheet.cell_value(row, 2)
            options = sheet.cell_value(row, 3)
            answer = sheet.cell_value(row, 4)

            if type == '单选题':
                options = [opt.strip() for opt in options.split(';') if opt.strip()]

            Question.objects.update_or_create(
                number=number,
                defaults={
                    'type': type,
                    'content': content,
                    'options': options,
                    'answer': answer
                }
            )

        self.stdout.write(self.style.SUCCESS(f'成功处理 {sheet.nrows-1} 条题目记录'))
