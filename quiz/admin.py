from django.contrib import admin
from .models import Question, WrongQuestion

admin.site.register(Question)
admin.site.register(WrongQuestion)
