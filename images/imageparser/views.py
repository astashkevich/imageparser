# -*- coding: utf-8 -*-
import gevent
import time

from PIL import Image
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, TemplateView
from multiprocessing.dummy import Pool
from .models import Site, Photo
from .utils import url_validate, image_parser, get_image, read_image, create_images, get_name


def index(request):
    template = "index.html"
    errors = []

    if request.method == 'POST':
        print(request.POST)
        q = request.POST.get('q', None)
        if q is None or q == '':
            errors.append('Enter web-site URL')
        else:
            start = time.clock()
            url = url_validate(q)
            if not url:
                errors.append('Invalid URL')
            else:
                name = get_name(url)
                site = Site(name=name) #create site instance
                site.save()

                jobs = [gevent.spawn(read_image, image_url) for image_url in image_parser(url)]
                gevent.joinall(jobs)

                images = ((site,) + job.value  for job in jobs if job.value)

                #start = time.clock()
                pool = Pool(4)
                pool.map(create_images, images)
                pool.close()
                pool.join()
                print(time.clock() - start)
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