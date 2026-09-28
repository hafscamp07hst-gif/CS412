from django.urls import path
from .views import ShowAllView, ArticleView, RandomArticleView

 
urlpatterns = [
    # map the URL (empty string) to the view
    path('show_all', ShowAllView.as_view(), name='show_all'), # generic class-based view
    path('', RandomArticleView.as_view(), name='random'), # generic class-based view

    path('article/<int:pk>' , ArticleView.as_view(), name = 'article'), #giving each urls for each quote
]