#! /usr/bin/python2.7
# -*- coding: utf-8 -*-

from flask import Flask, redirect, render_template, request, url_for
from werkzeug.contrib.atom import AtomFeed

from crawl import get_new_cars

PORT = 50030

app = Flask(__name__)

@app.route('/')
def home():
    return redirect(url_for('rss_encar'))

@app.route('/rss/encar.atom')
def rss_encar():
    articles = get_new_cars()

    feed = AtomFeed(u'엔카 - 쏘울 신규매물',
            feed_url=request.url,
            url=request.url_root)
    for article in articles:
        feed.add(**article)
    return feed.get_response()

if __name__ == '__main__':
    app.run(port=PORT, debug=True)
