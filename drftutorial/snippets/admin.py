from django.contrib import admin

from drftutorial.snippets.models import Snippet


class SnippetAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None,
            {
                'fields': ['title', 'language', 'style', 'owner', 'code'],
            },
        ),
        (
            'Highlighted',
            {
                'classes': ['collapse'],
                'fields': ['highlighted'],
            }
        )
    ]
    readonly_fields = ['highlighted']

    list_display = ['title', 'language', 'style', 'owner', 'linenos']
    list_filter = [
        ('linenos', admin.BooleanFieldListFilter),
        'owner',
        'language', 'style',
    ]
    ordering = ['-created']
    search_fields = ['title', 'code']

admin.site.register(Snippet, SnippetAdmin)
