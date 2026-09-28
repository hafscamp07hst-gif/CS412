from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Article
import random
# Create your views here.
class ShowAllView(ListView):
    '''Create a subclass of ListView to display all blog articles.'''
 
 
    model = Article # retrieve objects of type Article from the database
    template_name = 'blog/show_all.html'
    context_object_name = 'articles' # how to find the data in the template file


class ArticleView(DetailView):
    '''Display a single article.'''

    model = Article
    template_name = 'blog/article.html'
    context_object_name = 'article'

class RandomArticleView(DetailView):
    '''display random single article'''

    model = Article
    template_name = 'blog/article.html'
    context_object_name = 'article'


    #methods
    def get_object(self):

        all_articles = Article.objects.all()
        article = random.choice(all_articles)
        return article
