
from io import BytesIO
import os

from PIL import Image
from django.db import models
from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models
from django.db.models.signals import pre_delete, pre_save
from django.dispatch.dispatcher import receiver


def upload_to(instance, filename):
	return 'images/%s/%s'%(instance.site.name.split("/")[0], filename)

def thumb_upload_to(instance, filename):
	return 'images/%s/thumbnail/%s'%(instance.site.name.split("/")[0], filename)


class Site(models.Model):

	name = models.CharField(u'Название сайта', max_length=128)
	date_created = models.DateTimeField(auto_now_add=True)
	order = models.IntegerField(u'Порядок', default=0)

	def get_photos(self):
		return Photo.objects.filter(site=self)

	def __str__(self):
		return self.name

	class Meta:
		verbose_name_plural = "Sites"
		ordering = ['order']


class Photo(models.Model):
	name = models.CharField(u'Название изображения', max_length=255)
	date_modified = models.DateTimeField(auto_now=True)
	image = models.ImageField(upload_to=upload_to)
	image_thumbnail = models.ImageField(upload_to=thumb_upload_to)
	site = models.ForeignKey('Site', verbose_name=u'Сайт', on_delete=models.CASCADE)

	def __str__(self):
		return self.name

	class Meta:
		verbose_name_plural = "Gallery photo "
		ordering = ['site', 'name']


@receiver(pre_delete, sender=Photo)
def image_delete(sender, instance, **kwargs):
	"""
	delete image and image_thumbnail from file-system
	when deleting it from admin panel
	"""
	instance.image.delete(False)
	try:
		instance.image_thumbnail.delete(False)
	except sender.DoesNotExist:
		pass


# @receiver(pre_save, sender=Photo)
# def image_save_aupdate(sender, instance, *args, **kwargs):
# 	"""
# 	delete old image and image_thumbnail from file-system
# 	when updating it from admin panel, then call photo method
# 	create_thumbnail() for new image
# 	"""
# 	# if instance.pk:
# 	# 	try:
# 	# 		old=sender.objects.get(id=instance.id)
# 	# 	except sender.DoesNotExist:
# 	# 		return
# 	# 	if old.image and instance.image and old.image != instance.image:
# 	# 		old.image.delete(False)
# 	# 		if sender == Photo:
# 	# 			try: old.image_thumbnail.delete(False)
# 	# 			except sender.DoesNotExist:
# 	# 				pass
# 	# #instance.image_resize()
# 	# if sender == Photo:
# 	instance.create_thumbnail()