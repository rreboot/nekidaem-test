from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.views.generic import View

from django.db.models import Q
from django.urls import reverse

from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Post, Contact
from .forms import PostForm

from django.views.generic import ListView
from django.views.generic import DetailView

from django.http import HttpResponseRedirect

# TODO: Create Mixins!


class PostList(ListView):
    model = Post
    extra_context = {'title': 'Posts list',
                     'header': 'All posts'}


class UserList(ListView):
    model = User
    template_name = 'blog/user_list.html'
    extra_context = {'title': 'Users list',
                     'header': 'Users'}


class PostViewed(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'blog/posts_viewed.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Viewed posts'
        context['header'] = 'Viewed posts'
        context['posts'] = self.get_queryset()
        return context

    def get_queryset(self):
        return self.request.user.views.all()


class PostDetail(DetailView):
    queryset = Post.objects.all()
    template_name = 'blog/post_detail.html'

    def get_object(self, queryset=None):
        obj = super().get_object()
        return obj


class MyPosts(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'blog/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'My feed'
        context['header'] = 'My feed'
        context['posts'] = self.get_queryset()
        return context

    def get_queryset(self):
        user = User.objects.get(pk=self.request.user.id)
        following = user.following.all()
        qs = Post.objects.filter(Q(author__in=following) | Q(author=user))
        return qs


class UserDetail(ListView):
    model = Post
    template_name = 'blog/user_blog.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['username'] = self.kwargs['username']
        context['userr'] = User.objects.get(username=self.kwargs['username'])
        context['posts'] = self.get_queryset()
        return context

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs['username'])
        qs = user.posts.all()
        return qs


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
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class ToggleViewedPost(View):
    def get(self, request, pk):
        post = get_object_or_404(Post, id=pk)
        current_user = User.objects.get(username=request.user.username)
        if post.viewed(current_user):
            post.viewed_by.remove(current_user)
        else:
            post.viewed_by.add(current_user)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


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

