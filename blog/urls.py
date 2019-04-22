from django.urls import path

from .views import *

urlpatterns = [
    path('', PostList.as_view(), name='posts_list_url'),
    path('blog/', MyPosts.as_view(), name='my_posts_url'),
    path('users/', UserList.as_view(), name='users_list_url'),
    path('users/<str:username>/', UserDetail.as_view(), name='user_detail_url'),
    path('users/<str:username>/follow/', ToggleFollowUser.as_view(), name='follow_user_url'),
    path('post/create/', PostCreate.as_view(), name='post_create_url'),
    path('post/viewed/', PostViewed.as_view(), name='post_viewed_list_url'),
    path('post/<int:pk>/', PostDetail.as_view(), name='post_detail_url'),
    path('post/<int:pk>/edit/', PostEdit.as_view(), name='post_edit_url'),
    path('post/<int:pk>/viewed/', ToggleViewedPost.as_view(), name='view_post_url'),
]
