from flask import Flask, redirect, url_for, session, request, jsonify
from flask_oauthlib.client import OAuth
from flask import render_template

import pprint
import os

# This code originally from https://github.com/lepture/flask-oauthlib/blob/master/example/github.py
# Edited by P. Conrad for SPIS 2016 to add getting Client Id and Secret from
# environment variables, so that this will work on Heroku.
# Edited by S. Adams for Designing Software for the Web to add comments and remove flash messaging

app = Flask(__name__)

app.debug = True #Change this to False for production

app.secret_key = os.environ['SECRET_KEY'] 
os.environ['OAUTHLIB_INSECURE_TRANSPORT']='1'
oauth = OAuth(app)

#Set up Github as the OAuth provider
github = oauth.remote_app(
    'github',
    consumer_key=os.environ['GITHUB_CLIENT_ID'], 
    consumer_secret=os.environ['GITHUB_CLIENT_SECRET'],
    request_token_params={'scope': 'user:email'}, #request read-only access to the user's email.  For a list of possible scopes, see developer.github.com/apps/building-oauth-apps/scopes-for-oauth-apps
    base_url='https://api.github.com/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://github.com/login/oauth/access_token',  
    authorize_url='https://github.com/login/oauth/authorize' #URL for github's OAuth login
)


@app.context_processor
def inject_logged_in():
    return {"logged_in":('github_token' in session)}

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login')
def login():   
    return github.authorize(callback=url_for('authorized', _external=True, _scheme='http'))

@app.route('/logout')
def logout():
    session.clear()
    message='You were logged out'
    return render_template('home.html', message=message)

@app.route('/login/authorized')#the route should match the callback URL registered with the OAuth provider
def authorized():
    resp = github.authorized_response()
    if resp is None:
        session.clear()
        message = 'Access denied: reason=' + request.args['error'] + ' error=' + request.args['error_description'] + ' full=' + pprint.pformat(request.args)      
    else:
        try:
            print(resp)
            session['github_token'] = (resp['access_token'], '')
            session['user_data'] = github.get('user').data
            #Change requirements to login
            if github.get('user').data['public_repos'] > 15:
                message = 'You were successfully logged in as ' + session ['user_data']['login'] + '.'
            else:
                session.clear()
                message = 'You do not fill requirements to login.'
        except Exception as inst:
                session.clear()
                message = 'unable to login. Please try again.'
    return render_template('home.html', message=message)


@app.route('/Moonlit', methods = ['POST'])
def renderMoonlit():
    post = request.post['message']
    print(post)
    return render_template('Moonlit.html')


@app.route('/Mushroom', methods = ['POST'])
def renderMushroom():
    return render_template('Mushroom.html')
    
@app.route('/Sakura', methods = ['POST'])
def renderSakura():
    return render_template('CherryBlossom.html')


@github.tokengetter
def get_github_oauth_token():
    return session['github_token']


if __name__ == '__main__':
    app.run()
