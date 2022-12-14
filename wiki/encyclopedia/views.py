from django.shortcuts import render
from django import forms
from django.http import HttpResponseRedirect
from django.urls import reverse
import markdown
import random

from . import util

class NewPageForm(forms.Form):
    title = forms.CharField(label="Title")
    content = forms.CharField(widget=forms.Textarea(attrs={"rows":"5"}))

def convert_md_to_html(title):
    content = util.get_entry(title)
    markdowner = markdown.Markdown()
    if content == None:
        return None
    else:
        return markdowner.convert(content)

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, entry):
    html_content = convert_md_to_html(entry)
    if entry.lower() not in util.list_entries():

        request.session["entries"] = []
        for page in util.list_entries():
            if entry.lower() in page.lower():
                request.session["entries"] += [page]

        if len(request.session["entries"]) > 0:
            return render(request, "encyclopedia/substring.html", {
                "entry": entry,
                "entries": request.session["entries"]
            })
        else:
            return render(request, "encyclopedia/error.html", {
                "entry": entry
            })
    else:
        return render(request, "encyclopedia/entry.html", {
            "entry": html_content,
            "title": entry
        })

def search(request):
    search_post = request.GET.get('q', '')
    return entry(request, search_post)

def newpage(request):
    if request.method == "POST":
        form = NewPageForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            if title.lower() not in util.list_entries():
                util.save_entry(title, content)
                return HttpResponseRedirect(reverse("encyclopedia:entry", kwargs={"entry": title}))
            else: 
                return render(request, "encyclopedia/newpage.html", {
                    "exist": True,
                    "title": title,
                    "form": form
                })
        else:
            return render(request, "encyclopedia/newpage.html", {
                "exist": False,
                "form": form
            })
    return render(request, "encyclopedia/newpage.html", {
        "form": NewPageForm
    })

def edit(request):
    if request.method == 'POST':
        title = request.POST["entry_title"]
        content = util.get_entry(title)
        return render(request, "encyclopedia/edit.html", {
            "title": request.POST["entry_title"],
            "content": content,
        })

def save_edit(request):
    if request.method == 'POST':
        title = request.POST['title']
        content = request.POST['content']
        util.save_entry(title, content)
        html_content = convert_md_to_html(title)
        return render(request, "encyclopedia/entry.html", {
            "entry": html_content,
            "title": entry
        })

def rand(request):
    allEntries = util.list_entries()
    randomEntry = random.choice(allEntries)
    html_content = convert_md_to_html(randomEntry)
    return render(request, "encyclopedia/entry.html", {
        "title": randomEntry,
        "entry": html_content
    })