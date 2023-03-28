from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
# from django.http import HttpResponse
from .models import Post, Group, User, Follow
from .forms import PostForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page

POSTS_ON_MAIN = 10


# Паджинатор
def get_page_context(request, post_list):
    paginator = Paginator(post_list, POSTS_ON_MAIN)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


# Главная страница
@cache_page(20, key_prefix='index_page')
def index(request):
    title = 'Последние обновления на сайте'
    post_list = Post.objects.all()
    page_obj = get_page_context(request, post_list)
    context = {
        'posts': post_list,
        'title': title,
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


# Страница с постами (по группам)
def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    title = 'Записи сообщества'
    page_obj = get_page_context(request, posts)
    context = {
        'title': title,
        'group': group,
        'posts': posts,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


# Страница пользователя
def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = Post.objects.all().filter(author=author)
    page_obj = get_page_context(request, posts)
    if request.user.is_authenticated and Follow.objects.filter(
        user=request.user,
        author=author
    ).exists():
        following = True
    else:
        following = False
    context = {
        'author': author,
        'posts': posts,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


# Страница поста
def post_detail(request, post_id):
    one_post = get_object_or_404(Post, id=post_id)
    comments = one_post.comments.all()
    form = CommentForm()
    user = request.user.username
    author = one_post.author.username
    permit = user == author
    context = {
        'author': author,
        'permit': permit,
        'post_id': post_id,
        'one_post': one_post,
        'post_title': one_post.text,
        'comments': comments,
        'form': form,
    }
    return render(request, 'posts/post_detail.html', context)


# Страница создания нового поста
@login_required
def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST or None,
                        files=request.FILES or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', request.user.username)
    else:
        form = PostForm()
    return render(request, 'posts/create_post.html', {'form': form})


# @login_required
def post_edit(request, post_id):
    is_edit = True
    post = get_object_or_404(Post, pk=post_id)
    # Понимаю, что можно было использовать @login_required
    # просто в задании просили перенаправить нв post_detail
    # если пользователь не авторизован
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post.pk)
    else:
        if request.method == "POST":
            form = PostForm(request.POST or None,
                            files=request.FILES or None,
                            instance=post)
            if form.is_valid():
                post = form.save(commit=False)
                post.author = request.user
                post.save()
                return redirect('posts:post_detail', post_id=post.pk)
        else:
            form = PostForm(instance=post)
        return render(request, 'posts/create_post.html',
                      {'form': form, 'is_edit': is_edit})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    # информация о текущем пользователе доступна в переменной request.user
    posts = Post.objects.filter(author__following__user=request.user)
    page_obj = get_page_context(request, posts)
    context = {
        'page_obj': page_obj
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    # Подписаться на автора
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.create(
            user=request.user,
            author=author,
        )
    return redirect(
        'posts:profile',
        author.username
    )


@login_required
def profile_unfollow(request, username):
    # Дизлайк, отписка
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(
        user=request.user,
        author=author,
    ).delete()
    return redirect(
        'posts:profile',
        author.username
    )
