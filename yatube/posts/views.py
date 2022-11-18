from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group, User
from django.contrib.auth.decorators import login_required
from .forms import PostForm

P_COUNT = 10  # post count on page


def paginator_func(request, posts):
    paginator = Paginator(posts, P_COUNT)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def index(request):
    """Main page."""
    template = 'posts/index.html'
    posts = Post.objects.select_related('author', 'group')
    count = Post.objects.all().count
    context = {
        'page_obj': paginator_func(request, posts),
        'count': count
    }
    return render(request, template, context)


def group_posts(request, slug):
    """Group posts page."""
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    count = group.posts.all().count()
    posts = group.posts.all()
    context = {
        'group': group,
        'page_obj': paginator_func(request, posts),
        'count': count,
    }
    return render(request, template, context)


def profile(request, username):
    """Private user page."""
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    count = author.posts.all().count
    posts = author.posts.all()
    context = {
        'author': author,
        'count': count,
        'page_obj': paginator_func(request, posts)
    }
    return render(request, template, context)


def post_detail(request, post_id):
    """Post`s description and info."""
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    count = post.author.posts.all().count
    author = post.author
    context = {
        'count': count,
        'author': author,
        'post': post,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    """This page create a new post."""
    template = 'posts/create_post.html'
    form = PostForm(request.POST or None)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.author = request.user
        obj.save()
        return redirect('posts:profile', request.user)
    context = {
        'form': form,
    }
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    """This page edit a page."""
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect(
            'posts:post_detail', post_id
        )
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect(
            'posts:post_detail', post_id
        )
    return render(request, template, {
        'form': form, 'is_edit': True, 'post': post
    })
