from django.urls import path, include
from main import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('posts', views.PostViewSet, basename='post')
            #posts/  -> GET(list), POST(create)
            #posts/id/ -> GET(retrieve), PUT/PATCH(update), DELETE

urlpatterns = [
    path('', include(router.urls)),
    path('categories/', views.CategoryListView.as_view()),

    path('comments/', views.CommentlistCreateView.as_view()),
    path('comments/<int:pk>/', views.CommentDetailView.as_view()),
    # path('likes/', views.LikeCreateView.as_view()),
    # path('likes/<int:pk>/', views.LikeDeleteView.as_view()),
    # path('categories/', views.category_list),
    # path('categories1/', views.CategoryListView.as_view()),
    # path('posts/', views.PostListCreateView.as_view()),
    # path('posts/<int:pk>/', views.PostDetailView.as_view()),
]


#TODO likes
#TODO favorites
#TODO followers