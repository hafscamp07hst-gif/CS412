# File: quotes/views.py
# Author: Sung Tae Hwang (sthwang@bu.edu), 2026-09-16
# Description: Display Albert Camus quotes, images, and information.

import random

from django.shortcuts import render
from django.templatetags.static import static


quotes = [
    "Live to the point of tears.",
    "It is not the destination that moves me, but the path to get there.",
    "In the midst of winter, I found there was, within me, an invincible summer.",
]

images = [
    static("quotes/images/camus1.jpeg"),
    static("quotes/images/camus2.jpeg"),
    static("quotes/images/camus3.jpeg"),
]


def quote(request):
    """Display one randomly selected quote and image.

    """
    context = {
        "quote": random.choice(quotes),
        "image": random.choice(images),
    }

    return render(request, "quotes/quote.html", context)


def show_all(request):
    """Display every quote and image.

    """
    context = {
        "quotes": quotes,
        "images": images,
    }

    return render(request, "quotes/show_all.html", context)


def about(request):
    """Display information about Camus and the website creator.

    """
    return render(request, "quotes/about.html")