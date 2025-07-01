---
layout: default
title: Home
---

<div class="hero">
    <h1>{{ site.title }}</h1>
    <p class="hero-description">{{ site.description }}</p>
</div>

<div class="posts-grid">
    {% for post in site.posts %}
        <article class="post-card">
            <a href="{{ post.url | relative_url }}" class="post-link">
                {% assign post_images = site.static_files | where: "path", post.url %}
                {% assign image_name = post.title | append: "_0.webp" %}
                {% assign image_path = "/images/" | append: image_name %}
                
                <div class="post-image">
                    <img src="{{ image_path | relative_url }}" alt="{{ post.title }}" loading="lazy">
                </div>
                
                <div class="post-content">
                    <h2 class="post-title">{{ post.title }}</h2>
                    {% if post.date %}
                        <time class="post-date">{{ post.date | date: "%d %B %Y" }}</time>
                    {% endif %}
                    
                    <div class="post-excerpt">
                        {{ post.content | strip_html | truncatewords: 30 }}
                    </div>
                </div>
            </a>
        </article>
    {% endfor %}
</div>