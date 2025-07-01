---
layout: default
title: Home
---


<div class="posts-grid">
    {% for post in site.posts %}
        <article class="post-card">
            <a href="{{ post.url | relative_url }}" class="post-link">
                <div class="post-image">
                    <img src="{{ post.header_image | relative_url }}" alt="{{ post.title }}" loading="lazy">
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