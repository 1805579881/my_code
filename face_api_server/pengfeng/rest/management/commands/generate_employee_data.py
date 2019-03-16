import json

from django.core.management.base import BaseCommand, CommandError
import base64
from io import BytesIO

import numpy as np
from PIL import Image


def get_random_base64_image_str():
    img_array = np.random.rand(100, 100, 3) * 255
    img = Image.fromarray(img_array.astype('uint8')).convert('RGBA')
    buffer = BytesIO()
    img.save(buffer, format="png")
    img_str = base64.b64encode(buffer.getvalue())
    return img_str.decode('ascii')


class Command(BaseCommand):
    help = '生成仿真数据，保存至指定文件'

    def add_arguments(self, parser):
        parser.add_argument('num', type=int)

    def handle(self, *args, **options):
        num = options.get('num')
        if num:
            result = [{
                'name': 'BEJ' + str(i),
                'position': 'employee',
                'image': get_random_base64_image_str()
            } for i in range(num)]
            result_str = json.dumps(result, ensure_ascii=False, indent=4)
            self.stdout.write(self.style.SUCCESS(result_str))
        else:
            raise CommandError('请输入员工数量')
