import io
import os

import requests
from PIL import Image
from django.contrib import admin
from django.core.files.storage import default_storage
from fitz import fitz

from .models import MdsModel, Images, Decision

# Register your models here.


GCS_URL = 'https://storage.googleapis.com/mds_data/'

PATTERNS = {
    1: 'CD13_vs_CD11b',
    2: 'CD13_vs_CD16',
    3: 'CD11b_vs_CD16',
}

PIXEL_POSITIONS = {
    1: (205, 130, 1205, 1100),
    2: (1180, 130, 2180, 1100),
    3: (205, 1094, 1205, 2064),
}
IMAGE_LOCATION = 'pictures/'


def transform_to_images(pdf_file_url) -> [dict]:
    # Передается pdf файл, с двумя листами, который выгружается из калузы
    # Возвращает словарь с тремя уралими картинок для передачи в мэнеджер модели Image
    req = requests.get(pdf_file_url)
    pdf_file = fitz.open(stream=req.content, filetype="pdf")
    file_name = os.path.basename(pdf_file_url)
    # ПДФ начинается с числа, потом дефиз, получаем число до подчеркивания
    image_name = file_name.split('-')[0]
    # Загрузка второй страницы из .pdf и преобразование в Pixmap для сохранения
    page = pdf_file.load_page(1)
    pix = page.getPixmap(matrix=fitz.Matrix(300 / 72, 300 / 72))
    # Перевод в бинарный формат и открытие через PIL
    data = pix.getImageData("format")
    img = Image.open(io.BytesIO(data))
    # словарь для аутпута
    images_dict = dict()
    for number, pixels in PIXEL_POSITIONS.items():
        pattern_pic = img.crop(pixels)
        pattern_pic_url = f"{IMAGE_LOCATION}{image_name}_{PATTERNS.get(number)}.jpeg"
        file = default_storage.open(pattern_pic_url, 'w')
        pattern_pic.save(file, format=img.format)
        file.close()
        images_dict[number] = f"{GCS_URL}{pattern_pic_url}"

    print(images_dict)
    return images_dict


@admin.register(MdsModel)
class MdsModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'pdf_file', 'is_donor')

    def save_model(self, request, obj, form, change):

        obj.number = obj.pdf_file.name.split("-")[0]
        super(MdsModelAdmin, self).save_model(request, obj, form, change)

        file_name = obj.pdf_file.name
        pdf_file_url = f"{GCS_URL}{file_name}"
        images_dict = transform_to_images(pdf_file_url)
        for number, url in images_dict.items():

            Images.objects.create(
                case=obj,
                name=number,
                image=url
            )


@admin.register(Images)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('name', 'image', 'case')
    readonly_fields = ('name', 'image', 'case')


admin.site.register(Decision)
