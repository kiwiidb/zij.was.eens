---
layout: default
title: Home
---
<div class="search-container">
  <input type="text" id="search-input" placeholder="Search posts..." class="search-input">
  <ul id="results-container" class="search-results"></ul>
<script src="https://unpkg.com/simple-jekyll-search@latest/dest/simple-jekyll-search.min.js"></script>
<script>
  SimpleJekyllSearch({
    searchInput: document.getElementById('search-input'),
    resultsContainer: document.getElementById('results-container'),
    json: '/search.json',
    searchResultTemplate: '<li><a href="{url}" class="search-result-item"><h3>{title}</h3><p>{excerpt}</p><time>{date}</time></a></li>',
    noResultsText: '<li class="no-results">No results found</li>',
    limit: 10,
    fuzzy: false,
    exclude: ['url']
  })
</script>
</div>


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