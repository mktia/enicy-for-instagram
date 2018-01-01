# -*- coding: utf-8 -*-
import json
from flask import Flask, render_template, request, make_response, Response, redirect, url_for
from InstagramAPI import InstagramAPI

app = Flask(__name__)

basic_information = {
    'name': 'ENICY for Instagram',
    'url': 'https://instagram.enicy.co',
    'twitter': 'enicy_',
    'language_list': [
        {'code': 'ja', 'language': '日本語', 'locale': 'ja_JP'},
        {'code': 'en', 'language': 'English', 'locale': 'en_US'},
        {'code': 'id', 'language': 'Bahasa Indonesia', 'locale': 'id_ID'},
        {'code': 'pt', 'language': 'português', 'locale': 'pt_BR'},
        {'code': 'ru', 'language': 'русский язык', 'locale': 'ru_RU'},
        {'code': 'tr', 'language': 'Türkçe', 'locale': 'tr_TR'}
    ]
}


def return_html(html_file='index.html', lang='ja', friends=None, follows=None, followers=None, length=None):
    with open('static/' + lang + '.json', encoding='utf-8') as f:
        contents = json.load(f)

    # Attention: If we get the language code from cookie, the user cannot change it manually.
    response = make_response(render_template(
        html_file,
        info=basic_information,
        contents=contents,
        lang=lang,
        friends=friends,
        follows=follows,
        followers=followers,
        len=length
    ))
    response.set_cookie('language', value=lang)
    return response


@app.route('/')
def index():
    """Japanese"""
    return return_html()


@app.route('/en')
def index_en():
    """English"""
    return return_html(lang='en')


@app.route('/id')
def index_id():
    """Indonesian"""
    return return_html(lang='id')


@app.route('/pt')
def index_pt():
    """Portuguese"""
    return return_html(lang='pt')


@app.route('/ru')
def index_ru():
    """Russian"""
    return return_html(lang='ru')


@app.route('/tr')
def index_tr():
    """Turkish"""
    return return_html(lang='tr')


@app.route('/result', methods=['GET', 'POST'])
def result():
    """Return the lists of friends, follows_only, followed_only, and length"""

    # Set username and password
    __USERNAME = request.form['username']
    __PASSWORD = request.form['password']

    api = InstagramAPI(__USERNAME, __PASSWORD)
    api.setUser(__USERNAME, __PASSWORD)

    # Get the language code from cookie
    lang = request.cookies.get('language', None)

    if not api.login():
        print('Failed to login!')
        return redirect(url_for('login_error'))

    # Get follows
    api.getSelfUsersFollowing()
    follows = api.LastJson['users']

    # Get followers
    api.getSelfUserFollowers()
    followers = api.LastJson['users']

    api.logout()

    # The list of accounts you follow and be followed by
    friends = []
    # The list of accounts you follow but be not followed by
    follows_only = []
    # The list of accounts you don't follow but be followed by
    followed_only = []

    for i in follows:
        for j in followers:
            if i['username'] == j['username']:
                # If i is included in followers list, i is my friend.
                friends.append(i)
                # Remove i from followers list
                followers.remove(j)
                break
        else:
            # If i isn't included in followers list, he is added in follows_only list.
            follows_only.append(i)
    followed_only = followers

    # Save the number of users who each list includes
    length = {}

    length['friends'] = len(friends)
    length['follows_only'] = len(follows_only)
    length['followed_only'] = len(followed_only)

    return return_html(
        'result.html',
        lang=lang,
        friends=friends,
        follows=follows_only,
        followers=followed_only,
        length=length
    )


@app.route('/login_error')
def login_error():
    lang = request.cookies.get('language', None)
    return return_html('login_error.html', lang=lang)


@app.route('/contact')
def contact():
    return return_html('contact.html')


@app.route('/privacy')
def policy():
    return return_html('policy.html')


if __name__ == '__main__':
    app.run()
