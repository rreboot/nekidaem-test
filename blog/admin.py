from django.contrib import admin
from blog.models import Post
from django.contrib.auth.models import User


class PostAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(author=request.user)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'author':
            kwargs['queryset'] = User.objects.filter(username=request.user.username)
            kwargs['initial'] = request.user.username
            kwargs['disabled'] = False
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    exclude = ('viewed_by',)


admin.site.register(Post, PostAdmin)
