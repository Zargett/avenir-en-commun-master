
from random import choice
from django.shortcuts import render, redirect
import markdown
from .models import Chapter, Article, Measure, Part, UrlData
from haystack.query import SQ

from django.http import HttpResponse, HttpResponseNotFound, Http404
import os
from elasticsearch import Elasticsearch
from django.utils.html import strip_tags
import pandas as pd
from elasticsearch_dsl import Search
from elasticsearch_dsl.connections import connections
from elasticsearch_dsl import Q
import ast
import json
from django.conf import settings


import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


def home(request):
    return render(request, "newhome.html")
    return render(request, "home.html")

def measure(request,n,m):
    redirect(f'/s',n,"slfksksf",m)
def toc(request):

    return render(request, "toc.html",{
        'chapters': Chapter.objects.all(),
        'parts': Part.objects.all()

    })
def mentions(request):

    return render(request, "mentions-legales.html")
def part(request, n, slug=''):
    part = Part.objects.get(number=n)

    print(part.forewords)
    prev = None
    next = None
    print( part.main_title)
    try:
        prev  = Article.objects.get(id = int(part.id)-1)
        prev.desc = "Section précédente"
        prev.url = "/section/"
    except Article.DoesNotExist:
        prev = None
    if prev is None:
        try:
            print(part.id)
            prev = Part.objects.get(id=int(part.id) -1)

            prev.desc = "Partie précédente"
            prev.url = "/part/"
        except Part.DoesNotExist:
            prev = None


    try:
        next  = Article.objects.get(id = int(part.id)+2)
        next.desc = "Section suivante"
        next.url = "/section/"
    except Article.DoesNotExist:
        next = None
    if next is None:
        try:
            next = Part.objects.get(id = int(part.number)+1)
            next.desc = "Partie suivante"
            next.url = "/part/"
        except Part.DoesNotExist:
            next = None


    return render(request, "part.html", {
        'subject': part,
        'content': markdown.Markdown().convert(part.content),
        'next': next,
        'prev': prev,
        'book_navigation':None,
        'title' : part.title,
    })

def chapter(request, n, slug=''):
    chapter = Chapter.objects.get(number=n)
    prev = None
    next = None
    print( chapter.main_title)
    try:
        prev  = Article.objects.get(id = int(chapter.id)-1)
        prev.desc = "Section précédente"
        prev.url = "/section/"
    except Article.DoesNotExist:
        prev = None
    if prev is None:
        try:
            prev = Part.objects.get(number=int(chapter.part.number) -1)

            prev.desc = "Partie précédente"
            prev.url = "/part/"
        except Part.DoesNotExist:
            prev = None


    try:
        next  = Article.objects.get(id = int(chapter.id)+1)
        next.desc = "Section suivante"
        next.url = "/section/"
    except Article.DoesNotExist:
        next = None
    if next is None:
        try:
            next = Part.objects.get(number = int(chapter.part.number)+1)
            next.desc = "Partie suivante"
            next.url = "/part/"
        except Part.DoesNotExist:
            next = None


    return render(request, "chapter.html", {
        'subject': chapter,
        'content': markdown.Markdown().convert(chapter.text),
        'next': next,
        'prev': prev,
        'book_navigation':None,
        'title' : chapter.sub_title,
    })

def section(request, n, slug,m='None'):

    article = Article.objects.get(number=n)
    res = article.measures
    article.measures =  Measure.objects.filter(section_id= article.number).exclude(key=True)
    try:
      article.key =  Measure.objects.get(section_id= article.number,key=True)
    except Measure.DoesNotExist:
      article.key = None


    prev = None
    next = None

    #previous
    try:
        prev = Article.objects.get(id = int(article.id)-1)
        prev.desc = "Section précédente"
        prev.url = "/section/"
    except Article.DoesNotExist:
        prev = None
    if prev is None:
        try:
            prev = Chapter.objects.get(number = int(article.chapter.number) -1)
            print(prev.title)
            if prev is not None:
                prev = Article.objects.get(number = int(article.number)-1)
                prev.desc = "Section précédente"
                prev.url = "/section/"
        except Chapter.DoesNotExist:
            prev = None
    if prev is None:
        try:
            prev = Part.objects.get(number = int(article.chapter.part.number)-1)
            prev.desc = "Partie précédente"
            prev.url = "/part/"
        except Part.DoesNotExist:
            prev = None


    #next
    try:
         next = Article.objects.get(id = int(article.id)+1)
         next.desc = "Section suivante"
         next.url = "/section/"
    except Article.DoesNotExist:
        next = None
    if next is None:
        try:
            next = Part.objects.get(number = int(article.id)+1)
            next.desc = "Partie suivante"
            next.url = "/part/"
        except Part.DoesNotExist:
            next = None
    if next is None:
        try:
            next = Chapter.objects.get(number = int(article.chapter.number) +1)
            if next is not None:
                next = Article.objects.get(number = int(article.number)+1)
                next.desc = "Section suivante"
                next.url = "/section/"
        except Chapter.DoesNotExist:
            next = None



    searchterms = request.GET.get('q','').replace(',','|')
    def highlight(item):
        return re.sub(r'('+searchterms+')',r'<mark>\1</mark>',item)
    if searchterms and article.forewords:
        article.forewords = highlight(article.forewords)
    if article.key:
        article.key.text_high = highlight(article.key.text) if searchterms else article.key.text
    if article.measures:
        for m in article.measures:
            m.text_high = highlight(m.text) if searchterms else m.text
    if searchterms and article.title:
        article.title = highlight(article.title)
    #logging.warning(content)
    return render(request, "section.html", {
        'subject': article,
        'content': markdown.Markdown().convert(article.text),
        'next': next,
        'prev': prev,
        'book_navigation':None,
        'title' : article.title,
    })


def random(request):
    article = choice(list(Article.objects.all()))

    return redirect(f'/section/{article.number}/{article.slug}')


def fin(request):
    baseurl = request.build_absolute_uri()
    return render(request, "fin.html", { 'baseurl': baseurl })



def recherche(request):
    """My custom search view."""


    # further filter queryset based on some set of criteria
    req = request.GET.get('q','')
    #print(req)
  #  res  = queryset.filter(content_auto=req)
    #highlight = MyHighlighter(req, html_tag='mark', css_class='found', max_length=35)
    #for r in res:
        #   highlight.highlight(r.content)

        #  highlight.highlight(r.content)
    #elastic_client = Elasticsearch([settings.ELASTICSEARCH_HOST])
    #from core.models import ExternalPage
    #logging.warning(ExternalPage.objects.all())
    #elastic_client = Elasticsearch(['http://es:9200'])
    # create a Python dictionary for the search query:
    search_param = {
        "query": {
            "simple_query_string": {
                "query": req,
                "fields": ["title_auto","content_auto"],
                "default_operator": "or",
            }
            },
                "highlight" : {
                "require_field_match": True,
                "pre_tags" : ["<mark>"],
                    "post_tags" : ["</mark>"],
                "fields": {
                     "title": {
                "fragment_size": 300,
                     },
                 "content": {
                "fragment_size": 300,


            }
                }
    }
    }
    # get a response from the cluster
    #response = elastic_client.search(index="haystack", body=search_param)
    #logger.warning(response)

    connections.create_connection(hosts=[settings.ELASTICSEARCH_HOST], timeout=20)
    s = Search(index='haystack')
    q = Q("multi_match", query=req, fields=['title','content','title_auto','content_auto'],fuzziness=1, prefix_length=2)
    s = s.query(q).extra(from_=0, size=100)
    s = s.highlight('title', 'content','title_auto','content_auto',pre_tags=["<mark>"],post_tags=["</mark>"],require_field_match=True, number_of_fragments=1, fragment_size=300)
    s = s.execute()

    def extract_kw(s):
        kw = s.split('<mark>')
        keywords = []
        if len(kw)>1:
            for ss in kw[1:]:
                keywords.append(ss.split('</mark>')[0])
        return keywords
    for result in s:
        logging.warning(result.title+result.entity)
        keywords = []
        for f in ['content','title','content_auto','title_auto']:
            if f in result.meta.highlight:
                keywords += extract_kw(result.meta.highlight[f][0])
        result.keywords = sorted(list(set(keywords)),key=lambda x:len(x), reverse=True)


    return render(request, "recherche.html", {
        'query': s,
        'request' :req
    })



mesures_path = os.path.join('generation_visuels','mesures.json')
if os.path.exists(mesures_path):
    with open(mesures_path,'r') as f:
        mesures_dict = json.loads(f.read())
        mesures_list = sorted(list(mesures_dict.values()),key=lambda x:int(x['nmesure']))
else:
    mesures_dict = {}
    mesures_list = []

sections_path = os.path.join('generation_visuels','sections.json')
if os.path.exists(sections_path):
    with open(sections_path,'r') as f:
        sections_dict = json.loads(f.read())
else:
    sections_dict = {}


def shorten_text(txt,length):
    if len(txt)>length and length>3:
        txt = txt[:length-3] + '...'
    return txt

def redirect_short(request,n):
     content = UrlData.objects.get(slug=request.path)

     shortlink = 's{n}'.format(n=n)
     section = sections_dict.get(shortlink)
     if not section:
         return HttpResponseNotFound('<h1>Section inconnue</h1>')

     return render(request, "card.html", {
          'host': settings.PROD_HOST,
          'titre': shorten_text(re.sub(r'(\*)([^\*]+)\1',r'\2',section['chapitre']),50),
          'description': shorten_text(re.sub(r'(\*)([^\*]+)\1',r'\2',section['section']),124),
          'shortlink': shortlink,
          'redirect' : content.url
      })

     return redirect( content.url,n = n)

def redirect_short_measure(request,n,m=0):
     content = UrlData.objects.get(slug="/s"+n+"/")

     shortlink = 's{n}m{m}'.format(n=n,m=m)
     mesure = mesures_dict.get(shortlink)
     if not mesure:
         return HttpResponseNotFound('<h1>Mesure inconnue</h1>')

     return render(request, "card.html", {
         'host': settings.PROD_HOST,
         'titre': shorten_text(re.sub(r'(\*)([^\*]+)\1',r'\2',mesure['section']),50),
         'description': shorten_text(re.sub(r'(\*)([^\*]+)\1',r'\2',mesure['mesure']),124),
         'shortlink': shortlink,
         'redirect' : content.url+"#mesure-"+m
     })

#Title mesure & section : Nom de la section (si < 50 caractères sinon 47 premiers char + "...")
#Descr mesure : Texte de la mesure (si < 124 caractères sinon 121 premiers char + "...")
#Descr section : Texte de la section (si < 124 caractères sinon 121 premiers char + "...")



import os
import re
def visuel(request, v):
    couleurs = [
        ('#ed8f0e','#ffd397'), #1
        ('#32bf7c','#a9e7c9'), #2
        ('#f06e6e','#ffc7c7'), #3
        ('#412883','#aa9ec9'), #4
        ('#679ae7','#c0d6f7ff'), #5
    ]
    sections_path = os.path.join('generation_visuels','sections.json')
    if os.path.exists(sections_path):
        with open(sections_path,'r') as f:
            sections_dict = json.loads(f.read())
    else:
        sections_dict = {}

    mesures_path = os.path.join('generation_visuels','mesures.json')
    if os.path.exists(mesures_path):
        with open(mesures_path,'r') as f:
            mesures_dict = json.loads(f.read())
    else:
        mesures_dict = {}


    if v in sections_dict.keys():
        section  = sections_dict[v]
        background = 'mP{p}.png'.format(p=section['npartie'])
        section['couleurs'] = couleurs[section['npartie']-1]
        section['background'] = background
        section['section'] = re.sub(r'(\*)([^\*]+)\1',r'<span class="highlight">\2</span>',section['section'])
        return render(request,"visuels/section.html", section)
        #return render(request,"visuels/"+v+".html")

    if v in mesures_dict.keys():
        mesure  = mesures_dict[v]
        background = 'm{c}P{p}.png'.format(c='c' if mesure['cle'] else '',p=mesure['npartie'])
        mesure['couleurs'] = couleurs[mesure['npartie']-1]
        mesure['background'] = background
        mesure['section'] = re.sub(r'(\*)([^\*]+)\1',r'\2',mesure['section'])
        mesure['mesure'] = re.sub(r'(\*)([^\*]+)\1',r'<span class="highlight">\2</span>',mesure['mesure'])
        return render(request,"visuels/mesure.html", mesure)
    return HttpResponseNotFound('<h1>Pas de visuel</h1>')


grid_nbitems = 20

def grid(request):

    return render(request, "visuels/grid.html",dict(mesures=mesures_list[:grid_nbitems]))

def grid_page(request,p):
    return render(request, "visuels/grid_page.html",dict(mesures=mesures_list[(p-1)*grid_nbitems:p*grid_nbitems]))
