# Stage 1: Build the Jekyll site
FROM ruby:3.3-alpine AS builder

RUN apk add --no-cache build-base

WORKDIR /site

COPY Gemfile ./
RUN bundle install

COPY . .
RUN bundle exec jekyll build

# Stage 2: Serve with nginx
FROM nginx:alpine

COPY --from=builder /site/_site /usr/share/nginx/html

EXPOSE 80
