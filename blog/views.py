from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.views.generic import View

from django.db.models import Q
from django.urls import reverse

from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Post, Contact
from .forms import PostForm

from django.views.generic import ListView

from django.http import HttpResponseRedirect
# TODO: Create Mixins!


class PostList(ListView):
    model = Post
    extra_context = {'title': 'Posts list',
                     'header': 'All posts'}


class UserList(ListView):
    model = User
    extra_context = {'title': 'Users list',
                     'header': 'Users'}


class MyPosts(LoginRequiredMixin, View):
    def get(self, request):
        current_user = User.objects.get(pk=request.user.id)
        following = current_user.following.all()
        posts = Post.objects.filter(Q(author__in=following) | Q(author=current_user))
        return render(request, 'blog/index.html', context={'title': 'My feed',
                                                           'header': 'My feed',
                                                           'posts': posts})


class UserDetail(View):
    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        posts = user.posts.all()
        return render(request, 'blog/user_blog.html', context={'posts': posts,
                                                               'username': username})


class ToggleFollowUser(View):
    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        current_user = User.objects.get(username=request.user.username)

        if user in current_user.following.all():
            contact = Contact.objects.get(user_from=current_user, user_to=user)
            posts = Post.objects.filter(author=user).all()
            for post in posts:
                post.viewed_by.remove(current_user)
            contact.delete()
        else:
            Contact.objects.create(user_from=current_user, user_to=user)
        return redirect(reverse('user_detail_url', kwargs={'username': username}))


class ToggleViewedPost(View):
    def get(self, request, pk):
        post = get_object_or_404(Post, id=pk)
        current_user = User.objects.get(username=request.user.username)
        if post.viewed(current_user):
            post.viewed_by.remove(current_user)
        else:
            post.viewed_by.add(current_user)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class PostDetail(View):
    def get(self, request, pk):
        post = get_object_or_404(Post, id=pk)
        return render(request, 'blog/post_detail.html', context={'post': post})


class PostCreate(LoginRequiredMixin, View):
    form_class = PostForm
    template_name = 'blog/post_create_form.html'

    def get(self, request):
        form = self.form_class
        return render(request, self.template_name, context={'form': form})

    def post(self, request):
        bound_form = self.form_class(request.POST)

        if bound_form.is_valid():
            post = bound_form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect(post)
        return render(request, self.template_name, context={'form': bound_form})


class PostEdit(LoginRequiredMixin, View):
    def get(self, request, pk):
        post = get_object_or_404(Post, id=pk)
        print(post.author.username)
        print(request.user.username)
        bound_form = PostForm(instance=post)
        return render(request, 'blog/post_edit_form.html', context={'form': bound_form,
                                                                    'pk': pk})

    def post(self, request, pk):
        post = get_object_or_404(Post, id=pk)
        if post.author.username == request.user.username:
            bound_form = PostForm(request.POST, instance=post)

            if bound_form.is_valid():
                post = bound_form.save(commit=False)
                post.author = request.user
                post.save()
                return redirect(post)
            return render(request, 'blog/post_edit_form.html', context={'form': bound_form,
                                                                        'pk': pk})
        else:
            return redirect(post)


class PostViewed(LoginRequiredMixin, View):
    def get(self, request):
        current_user = request.user
        posts = current_user.views.all()
        return render(request, 'blog/posts_viewed.html', context={'posts': posts})