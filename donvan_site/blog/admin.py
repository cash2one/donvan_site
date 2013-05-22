from django.contrib import admin
from blog.models import Post, Tag, Category, Link, UploadFile
from mptt.admin import MPTTModelAdmin
from django.db.models import get_model
from blog.forms import PostAdminModelForm


class PostAdmin(admin.ModelAdmin):

    fields = (('title', 'visible'), 'content', ('tag',), ('category', 'status'))
    list_display = ('title', 'brief', 'postTag', 'category', 'publish_time', 'update_time', 'status', 'visible', 'view_count')
    date_hierarchy = 'publish_time'
#     list_editable = ('status', 'visible', 'category')
    list_per_page = 50
    search_fields = ['title', 'content']
    ordering = ('-publish_time',)
    form = PostAdminModelForm
#    filter_horizontal = ('tag', )
#    filter_vertical = ('tag', )
#    list_max_show_all = 100
#     def formfield_for_foreignkey(self, db_field, request, **kwargs):
#         if db_field.name == "category":
#             kwargs["queryset"] = Category.objects.all()
#         return super(PostAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
admin.site.register(get_model('blog', 'post'), PostAdmin)


class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'content', 'postCount')
#     list_editable = ('content',)
    ordering = ('-id',)
admin.site.register(Tag, TagAdmin)


class CategoryAdmin(MPTTModelAdmin):
    list_display = ('id', 'parent', 'content', 'postCount')
#     list_editable = ('parent', 'content',)
    mptt_indent_field = 'content'
admin.site.register(Category, CategoryAdmin)


class LinkAdmin(admin.ModelAdmin):

    list_display = ('id', 'name', 'url')
#     list_editable = ('name', 'url')
admin.site.register(Link, LinkAdmin)


class UploadFileAdmin(admin.ModelAdmin):
    fields = ('file', 'description')
    list_display = ('description', 'file_path', 'size', 'create_time')
    search_fields = ['description', 'file_path']
    date_hierarchy = 'create_time'
    ordering = ['create_time']
admin.site.register(UploadFile, UploadFileAdmin)