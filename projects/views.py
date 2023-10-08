from django.db import IntegrityError
from django.shortcuts import render, redirect
from .models import Project
from .forms import ProjectForm, ReviewForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib import messages


def projects(request):
    page = request.GET.get('page')
    results = 3
    all_projects = Project.objects.all()
    paginator = Paginator(all_projects, results)
    try:
        all_projects = paginator.page(page)
    except PageNotAnInteger:
        page = 1
        all_projects = paginator.page(page)
    except EmptyPage:
        page = paginator.num_pages
        all_projects = paginator.page(page)

    page = int(page)
    left_index = page - 3 if page > 3 else 1

    right_index = page + 4 if page < paginator.num_pages - 3 else paginator.num_pages + 1

    custom_range = range(left_index, right_index)
    context = {'projects': all_projects, 'paginator': paginator, 'custom_range': custom_range}
    return render(request, 'projects/projects.html', context)


def project(request, pk):
    one_project = Project.objects.get(pk=pk)
    form = ReviewForm()
    try:
        if request.method == 'POST':
            if request.user.profile == one_project.owner:
                messages.error(request, 'You can`t leave a comment on your own project!')
                return redirect('project', pk=one_project.id)
            else:
                form = ReviewForm(request.POST)
                review = form.save(commit=False)
                review.project = one_project
                review.owner = request.user.profile
                review.save()
                one_project.get_vote_count()

                messages.success(request, 'Your review was posted successfully!')
                return redirect('project', pk=one_project.id)
    except IntegrityError:
        messages.error(request, 'You have already posted the comment!')
        return redirect('project', pk=one_project.id)

    context = {'project': one_project, 'form': form}
    return render(request, 'projects/single-project.html', context)


@login_required(login_url='login')
def create_project(request):
    profile = request.user.profile
    form = ProjectForm()
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            user_project = form.save(commit=False)
            user_project.owner = profile
            user_project.save()
            return redirect('account')

    context = {'form': form}
    return render(request, 'projects/create-project.html', context)


@login_required(login_url='login')
def update_project(request, pk):
    profile = request.user.profile
    prjct = profile.project_set.get(pk=pk)
    form = ProjectForm(instance=prjct)

    if request.method == "POST":
        form = ProjectForm(request.POST, request.FILES, instance=prjct)
        if form.is_valid():
            form.save()
            return redirect('account')

    context = {'form': form, 'project': prjct}
    return render(request, 'projects/form-template.html', context)


@login_required(login_url='login')
def delete_project(request, pk):
    profile = request.user.profile
    prjct = profile.project_set.get(pk=pk)

    if request.method == 'POST':
        prjct.delete()
        return redirect('account')

    context = {'object': prjct}
    return render(request, 'projects/delete.html', context)
