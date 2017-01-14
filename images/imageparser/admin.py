from django.contrib import admin

# Register your models here.
from .models import  Site, Photo


class PhotoInline(admin.TabularInline):
	model = Photo
	extra = 0
	exclude = ('image_thumbnail',)
	readonly_fields = ('get_photo', 'date_modified')

	def get_photo(self, obj):
		return u'<img src="%s" width="100" />' % obj.image_thumbnail.url
	get_photo.short_description = 'Preview'
	get_photo.allow_tags = True



class SiteAdmin(admin.ModelAdmin):
	inlines = [PhotoInline,]

	list_display = ('name', 'date_created', 'order')


admin.site.register(Site, SiteAdmin)