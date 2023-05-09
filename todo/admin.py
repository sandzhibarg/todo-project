from django.contrib import admin
from .models import Todo

# класс который выводит поле created модели Todo (по умолчанию данное поле не выводится в админ панели)
class TodoAdmin(admin.ModelAdmin):
    readonly_fields = ('created',)

# Register your models here.
admin.site.register(Todo, TodoAdmin)