from django.contrib import admin

from .models import (
    CustomUser,
    Unit,
    Ingredient,
    Tag,
    Recipe,
    Subscribe
)

admin.site.register(CustomUser)
admin.site.register(Unit)
admin.site.register(Ingredient)
admin.site.register(Tag)
admin.site.register(Recipe)
admin.site.register(Subscribe)