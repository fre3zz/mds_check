from django.db import models

from .validators import validate_file_extension

# Create your models here.
# 3 варианта анализируемых паттернов
PATTERNS = (
        (1, 'CD13_vs_CD11b'),
        (2, 'CD13_vs_CD16'),
        (3, 'CD11b_vs_CD16'),
    )
# Донор или нет для выбора в форме
IS_DONOR = (
        (True, 'donor'),
        (False, 'patient'),
    )

# Варианты ответов
DECISIONS = [
        ('pos', 'abnormal'),
        ('neg', 'normal'),
        ('na', 'no idea'),
        ('pnh', 'PNH'),
    ]

# Статус отвечающего
RESPONDER = (
        ('exp', 'expert'),
        ('bio', 'biologist'),
        ('md', 'doctor'),
        ('nov', 'novice'),
    )


class MdsModel(models.Model):

    pdf_file = models.FileField(upload_to='pdf', validators=[validate_file_extension], unique=True)
    is_donor = models.BooleanField(default=False, choices=IS_DONOR)
    number = models.IntegerField(default=0)

    def __str__(self):
        return self.pdf_file.name


class Images(models.Model):

    name = models.CharField(max_length=1, choices=PATTERNS, default=None, null=False)
    image = models.URLField()
    case = models.ForeignKey(MdsModel, on_delete=models.CASCADE, related_name='images')

    def __str__(self):
        return f"{self.name}: '{self.image}'"


class Decision(models.Model):

    decision = models.CharField(max_length=3, choices=DECISIONS, default='na', null=False)
    image = models.ForeignKey(Images, on_delete=models.CASCADE, related_name='decisions')
    is_expert = models.BooleanField(default=False)
    responder = models.CharField(max_length=3, choices=RESPONDER, default='bio', null=False)
    responder_email = models.EmailField(null=False, default="")
    posted_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.decision} decision on {self.image}"
