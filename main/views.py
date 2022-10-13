from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import APIView
from rest_framework import generics, permissions
from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from . import serializers
from main.models import Category, Post, Comment, Like, Favorites
from .permissions import IsAuthor


class StandartResultPagination(PageNumberPagination):
    page_size = 3
    page_query_param = 'page'
    max_page_size = 1000


class CategoryListView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = serializers.CategorySerializer


class PostViewSet(ModelViewSet):
    queryset = Post.objects.all()
    pagination_class = StandartResultPagination
    filter_backends = (SearchFilter,)
    search_fields = ('title', )
    filter_backends = (SearchFilter, DjangoFilterBackend)
    filterset_fields = ('owner', 'category')

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return serializers.PostCreateSerializer
        elif self.action == 'retrieve':
            return serializers.PostSerializer
        else:
            return serializers.PostListSerializer

    def get_permissions(self):
        #изменять и удалять пост может только автор
        if self.action in ('update', 'partial_update', 'destroy'):
            return [permissions.IsAuthenticated(), IsAuthor()]
        #создавать может только залогиненный юзер
        elif self.action in ('create', 'add_to_liked', 'remove_from_liked', 'favorite_action'):
            return [permissions.IsAuthenticated()]
        #просматривать могут все
        else:
            return [permissions.AllowAny()]

    @action(['GET'], detail=True)
    def comments(self, request, pk):
        post = self.get_object()
        comments = post.comments.all()
        serializer = serializers.CommentSerializers(comments, many=True)
        return Response(serializer.data, status=200)

    # /posts/id/add_to_liked/
    @action(['POST'], detail=True)
    def add_to_liked(self, request, pk):
        post = self.get_object()
        user = request.user
        if user.liked.filter(post=post).exists():
            return Response('This post is already liked!', status=400)
        Like.objects.create(owner=user, post=post)
        return Response('You liked the post', status=201)

# class PostListCreateView(generics.ListCreateAPIView):
#     queryset = Post.objects.all()
#     permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
#
#     def get_serializer_class(self):
#         if self.request.method == 'GET':
#             return serializers.PostListSerializer
#         return serializers.PostCreateSerializer
#
#     def perform_create(self, serializer):
#         serializer.save(owner=self.request.user)


# class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Post.objects.all()
#
#     def get_permissions(self):
#         if self.request.method in ('PUT', 'PATCH', 'DELETE'):
#             return [permissions.IsAuthenticated(), IsAuthor()]
#         return [permissions.AllowAny()]
#
#     def get_serializer_class(self):
#         if self.request.method in ('PUT', 'PATCH'):
#             return serializers.PostCreateSerializer
#         return serializers.PostSerializer


    # /posts/<id>/remove_from_liked/
    @action(['DELETE'], detail=True)
    def remove_from_liked(self, request, pk):
        post = self.get_object()
        user = request.user
        if not user.liked.filter(post=post).exists():
            return Response('You didn\'t liked this post!', status=400)
        user.liked.filter(post=post).delete()
        return Response('Your like is deleted!', status=204)

    @action(['GET'], detail=True)
    def get_likes(self, request, pk):
        post = self.get_object()
        likes = post.likes.all()
        serializer = serializers.LikeSerializer(likes, many=True)
        return Response(serializer.data, status=200)

    @action(['POST'], detail=True)
    def favorite_action(self, request, pk):
        post = self.get_object()
        user = request.user
        if user.favorites.filter(post=post).exists():
            user.favorites.filter(post=post).delete()
            return Response('Deleted from Favorites', status=204)
        Favorites.objects.create(owner=user, post=post)
        return Response('Added to Favorites!', status=201)


class CommentlistCreateView(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = serializers.CommentSerializers
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = serializers.CommentSerializers

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsAuthor()]


# class LikeCreateView(generics.CreateAPIView):
#     permission_classes = (permissions.IsAuthenticated,)
#     serializer_class = serializers.LikeSerializer
#
#     def perform_create(self, serializer):
#         serializer.save(owner=self.request.user)
#
#
# class LikeDeleteView(generics.DestroyAPIView):
#     queryset = Like.objects.all()
#     permission_classes = (permissions.IsAuthenticated, IsAuthor)


# function based view
# @api_view(["GET"])
# def category_list(request):
#     queryset = Category.objects.all()
#     serializer = serializers.CategorySerializer(queryset, many=True)
#     return Response(data=serializer.data, status=200)


# class based view(APIview)
# class CategoryListView(APIView):
#     def get(self, request):
#         queryset = Category.objects.all()
#         serializer = serializers.CategorySerializer(queryset, many=True)
#         return Response(serializer.data, status=200)
#
#     def post(self, request):
#         serializer = serializers.CategorySerializer(data=request.data)
#         if serializer.is_valid(raise_exception=True):
#             serializer.save()
#             return Response(serializer.data, status=200)