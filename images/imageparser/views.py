# -*- coding: utf-8 -*-
from PIL import Image
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, TemplateView
from .models import Site, Photo
from .utils import url_validate, image_parser, get_image, get_name, get_filename, get_thumb, read_image


def index(request):
    template = "index.html"
    errors = []

    if request.method == 'POST':
        print(request.POST)
        q = request.POST.get('q', None)
        if q is None or q == '':
            errors.append('Enter web-site URL')
        else:
            url = url_validate(q)
            if not url:
                errors.append('Invalid URL')
            else:
                name = get_name(url)
                site = Site(name=name) #create site instance
                site.save()

                for image_url in image_parser(url):
                    image = read_image(image_url)
                    if not image:
                        continue
                    image_file = get_image(image)
                    thumb_file = get_thumb(image)
                    filename = get_filename(image_url)
                    uploaded_image = Photo(name=filename, site=site)
                    uploaded_image.image.save(filename, image_file)
                    uploaded_image.image_thumbnail.save('thumbnail_%s.%s'%(filename.split('.')[0], filename.split('.')[-1]), thumb_file)
                    uploaded_image.save()
                    image_file.close()
                return redirect('detail', pk=site.pk)

    return render(request, template, {'errors': errors})


class SitesList(ListView):
    model = Site
    template_name = 'list.html'
    context_object_name = 'sites'

    def get_context_data(self, **kwargs):
        context = super(SitesList, self).get_context_data(**kwargs)
        return context


class SiteDetail(DetailView):
    model = Site
    template_name = 'detail.html'
    context_object_name = 'site'

    def get_context_data(self, **kwargs):
        context = super(SiteDetail, self).get_context_data(**kwargs)
        site = Site.objects.get(pk=self.kwargs.get('pk'))
        return context


class Contact(TemplateView):
    template_name = "contact.html"