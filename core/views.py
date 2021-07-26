
from random import choice
from django.shortcuts import render, redirect
import markdown
from .models import Chapter, Article
from haystack.query import SQ

from elasticsearch import Elasticsearch
from django.utils.html import strip_tags
import pandas as pd
from elasticsearch_dsl import Search, connections
from elasticsearch_dsl import Q
def home(request):
    return render(request, "home.html")


def toc(request):
    print("passage par toc")
    return render(request, "toc.html",{
        'chapters': Chapter.objects.all()
       
    })


def chapter(request, n, slug):
    chapter = Chapter.objects.get(number=n)
    print("l'id est : " ,chapter.id)
    prev  = Article.objects.get(id = int(chapter.id)-1)
    next = Article.objects.get(id = int(chapter.id)+1)
    prev.desc = "Section précédente"
    next.desc = "Section suivante"
    return render(request, "chapter.html", {
        'subject': chapter,
        'content': markdown.Markdown().convert(chapter.content),
        'next': next,
        'prev': prev,
        'book_navigation':None,
    })



def section(request, n, slug):

    article = Article.objects.get(number=n)
    prev = None
    next = None
    try:
        prev = Article.objects.get(id = int(article.id)-1)
    except Article.DoesNotExist:
        prev = None
    if prev is None:
        prev = Chapter.objects.get(number = int(article.chapter.number)-1)
        prev.desc = "Chapitre précédent"
    else:
        prev.desc = "Section précédente"

    try:
         next = Article.objects.get(id = int(article.id)+1)
    except Article.DoesNotExist:
        next = None
    if next is None:
        next = Chapter.objects.get(number = int(article.chapter.number)+1)
        next.desc = "Chapitre suivant"
    else:
        next.desc = "Section suivante"
    return render(request, "section.html", {
        'subject': article,
        'content': markdown.Markdown().convert(article.content),
        'next': next,
        'prev': prev,
        'book_navigation':None,
    })


def random(request):
    article = choice(list(Article.objects.all()))

    return redirect(f'/section/{article.number}/{article.slug}')
  

def search(request):
    """My custom search view."""

   
    # further filter queryset based on some set of criteria     
    req = request.GET.get('q','')
    print(req)
  #  res  = queryset.filter(content_auto=req)
    #highlight = MyHighlighter(req, html_tag='mark', css_class='found', max_length=35)     
    #for r in res:
        #   highlight.highlight(r.content)
        
        #  highlight.highlight(r.content)
    elastic_client = Elasticsearch()
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
                     "title_auto": {
                "fragment_size": 300,
                "number_of_fragments": 100,

            }, 
              "content_auto": {
                "fragment_size": 300,
                "number_of_fragments": 100,

            }
                }
    }
    }
    # get a response from the cluster
    response = elastic_client.search(index="haystack", body=search_param)
    connections.create_connection(hosts=['localhost'], timeout=20)
    s = Search(index='haystack')
    q = Q("multi_match", query=req, fields=['title_auto','content_auto'])
    s = s.query(q).extra(from_=0, size=100)
    s = s.highlight('title_auto', 'content_auto',pre_tags=["<mark>"],post_tags=["</mark>"],require_field_match=False, number_of_fragments=1, fragment_size=250)
    s = s.execute()
    for h in s.hits:
        print(h)
        if hasattr(h.meta,'highlight'):
            if hasattr(h.meta.highlight,'title'):
                print(h.meta.highlight.title)
            if hasattr(h.meta.highlight,'content'):
                print(h.meta.highlight.content)

    return render(request, "search.html", {
        'query': s,
        'request' :req
    })
