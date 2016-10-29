from twilio.util import TwilioCapability
import twilio.twiml
import socket
import copy
import threading
import urllib
import urllib2
import os
import tailer
import sys
import datetime
from dateutil import tz
import time
import pip.utils.logging
import pip
import shutil
import codecs
import weakref
import types
import pkg_resources
import babel.dates
import pytz
import docassemble.base.parse
import docassemble.base.pdftk
import docassemble.base.interview_cache
import docassemble.webapp.update
from docassemble.base.standardformatter import as_html, signature_html
import docassemble.webapp.database
import tempfile
import zipfile
import traceback
from docassemble.base.pandoc import word_to_markdown, convertible_mimetypes, convertible_extensions
from docassemble.webapp.screenreader import to_text
from docassemble.base.error import DAError, DAErrorNoEndpoint, DAErrorMissingVariable
from docassemble.base.functions import pickleable_objects, word, comma_and_list, get_default_timezone
from docassemble.base.logger import logmessage
from Crypto.Hash import MD5
import mimetypes
import logging
import pickle
import string
import random
import cgi
import Cookie
import re
import urlparse
import json
import base64
import requests
import redis
from flask import make_response, abort, render_template, request, session, send_file, redirect, url_for, current_app, get_flashed_messages, flash, Markup, jsonify, Response, g
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from flask_user import login_required, roles_required, UserManager, SQLAlchemyAdapter
from flask_user.forms import LoginForm
from flask_user import signals, user_logged_in, user_changed_password, user_registered, user_registered, user_reset_password
from docassemble.webapp.develop import CreatePackageForm, CreatePlaygroundPackageForm, UpdatePackageForm, ConfigForm, PlaygroundForm, LogForm, Utilities, PlaygroundFilesForm, PlaygroundFilesEditForm, PlaygroundPackagesForm
from flask_mail import Mail, Message
import flask_user.signals
import httplib2
from werkzeug import secure_filename, FileStorage
from rauth import OAuth1Service, OAuth2Service
from flask_kvsession import KVSessionExtension
from simplekv.memory.redisstore import RedisStore
#from simplekv.db.sql import SQLAlchemyStore
from sqlalchemy import create_engine, MetaData, Sequence, or_, and_
from docassemble.webapp.app_and_db import app, db
from docassemble.webapp.backend import s3, initial_dict, can_access_file_number, get_info_from_file_number, get_info_from_file_reference, get_mail_variable, async_mail, get_new_file_number, pad, unpad, encrypt_phrase, pack_phrase, decrypt_phrase, unpack_phrase, encrypt_dictionary, pack_dictionary, decrypt_dictionary, unpack_dictionary, nice_date_from_utc, fetch_user_dict, fetch_previous_user_dict, advance_progress, reset_user_dict, get_chat_log
from docassemble.webapp.core.models import Attachments, Uploads, SpeakList, Supervisors#, Messages
from docassemble.webapp.users.models import UserAuth, User, Role, UserDict, UserDictKeys, UserRoles, UserDictLock, TempUser, ChatLog
from docassemble.webapp.packages.models import Package, PackageAuth, Install
from docassemble.base.config import daconfig, s3_config, S3_ENABLED, gc_config, GC_ENABLED, hostname, in_celery
from docassemble.webapp.files import SavedFile, get_ext_and_mimetype, make_package_zip
import docassemble.base.util
import yaml
import inspect
from subprocess import call, Popen, PIPE
DEBUG = daconfig.get('debug', False)
from pygments import highlight
from pygments.lexers import YamlLexer
from pygments.formatters import HtmlFormatter

default_playground_yaml = """metadata:
  title: Default playground interview
  short title: Test
  comment: This is a learning tool.  Feel free to write over it.
---
include:
  - basic-questions.yml
---
mandatory: true
question: |
  Here is your document, ${ client }.
subquestion: |
  In order ${ quest }, you will need this.
attachments:
  - name: Information Sheet
    filename: info_sheet
    content: |
      Your name is ${ client }.
      
      % if user.age_in_years() > 60:
      You are a senior.
      % endif
      Your quest is ${ quest }.  You
      are eligible for ${ benefits }.
---
question: |
  What is your quest?
fields:
  - Your quest: quest
    hint: to find the Loch Ness Monster
---
code: |
  if user.age_in_years() < 18:
    benefits = "CHIP"
  else:
    benefits = "Medicaid"
"""

app.debug = False

ok_mimetypes = {"application/javascript": "javascript", "text/x-python": "python", "application/json": "json"}
ok_extensions = {"yml": "yaml", "yaml": "yaml", "md": "markdown", "markdown": "markdown", 'py': "python", "json": "json"}
default_yaml_filename = daconfig.get('default_interview', 'docassemble.demo:data/questions/questions.yml')

document_match = re.compile(r'^--- *$', flags=re.MULTILINE)
fix_tabs = re.compile(r'\t')
fix_initial = re.compile(r'^---\n')
noquote_match = re.compile(r'"')
lt_match = re.compile(r'<')
gt_match = re.compile(r'>')
amp_match = re.compile(r'&')
extraneous_var = re.compile(r'^x\.|^x\[')

if 'mail' not in daconfig:
    daconfig['mail'] = dict()
default_title = daconfig.get('default_title', daconfig.get('brandname', 'docassemble'))
default_short_title = daconfig.get('default_short_title', default_title)
os.environ['PYTHON_EGG_CACHE'] = tempfile.mkdtemp()
PNG_RESOLUTION = daconfig.get('png_resolution', 300)
PNG_SCREEN_RESOLUTION = daconfig.get('png_screen_resolution', 72)
PDFTOPPM_COMMAND = daconfig.get('pdftoppm', 'pdftoppm')
DEFAULT_LANGUAGE = daconfig.get('language', 'en')
DEFAULT_LOCALE = daconfig.get('locale', 'US.utf8')
DEFAULT_DIALECT = daconfig.get('dialect', 'us')
LOGSERVER = daconfig.get('log server', None)
#message_sequence = dbtableprefix + 'message_id_seq'

audio_mimetype_table = {'mp3': 'audio/mpeg', 'ogg': 'audio/ogg'}

valid_voicerss_languages = {
    'ca': ['es'],
    'zh': ['cn', 'hk', 'tw'],
    'da': ['dk'],
    'nl': ['nl'],
    'en': ['au', 'ca', 'gb', 'in', 'us'],
    'fi': ['fi'],
    'fr': ['ca, fr'],
    'de': ['de'],
    'it': ['it'],
    'ja': ['jp'],
    'ko': ['kr'],
    'nb': ['no'],
    'pl': ['pl'],
    'pt': ['br', 'pt'],
    'ru': ['ru'],
    'es': ['mx', 'es'],
    'sv': ['se']
    }

voicerss_config = daconfig.get('voicerss', None)
if not voicerss_config or ('enable' in voicerss_config and not voicerss_config['enable']) or not ('key' in voicerss_config and voicerss_config['key']):
    VOICERSS_ENABLED = False
else:
    VOICERSS_ENABLED = True
ROOT = daconfig.get('root', '/')
#app.logger.warning("default sender is " + app.config['MAIL_DEFAULT_SENDER'] + "\n")
exit_page = daconfig.get('exitpage', 'http://docassemble.org')

SUPERVISORCTL = daconfig.get('supervisorctl', 'supervisorctl')
PACKAGE_CACHE = daconfig.get('packagecache', '/var/www/.cache')
WEBAPP_PATH = daconfig.get('webapp', '/usr/share/docassemble/webapp/docassemble.wsgi')
PACKAGE_DIRECTORY = daconfig.get('packages', '/usr/share/docassemble/local')
UPLOAD_DIRECTORY = daconfig.get('uploads', '/usr/share/docassemble/files')
FULL_PACKAGE_DIRECTORY = os.path.join(PACKAGE_DIRECTORY, 'lib', 'python2.7', 'site-packages')
LOG_DIRECTORY = daconfig.get('log', '/usr/share/docassemble/log')
#PLAYGROUND_MODULES_DIRECTORY = daconfig.get('playground_modules', )

for path in [FULL_PACKAGE_DIRECTORY, PACKAGE_CACHE, UPLOAD_DIRECTORY, LOG_DIRECTORY]: #, os.path.join(PLAYGROUND_MODULES_DIRECTORY, 'docassemble')
    if not os.path.isdir(path):
        try:
            os.makedirs(path)
        except:
            print "Could not create path: " + path
            sys.exit(1)
    if not os.access(path, os.W_OK):
        print "Unable to create files in directory: " + path
        sys.exit(1)
if not os.access(WEBAPP_PATH, os.W_OK):
    print "Unable to modify the timestamp of the WSGI file: " + WEBAPP_PATH
    sys.exit(1)

init_py_file = """try:
    __import__('pkg_resources').declare_namespace(__name__)
except ImportError:
    __path__ = __import__('pkgutil').extend_path(__path__, __name__)
"""
    
#if not os.path.isfile(os.path.join(PLAYGROUND_MODULES_DIRECTORY, 'docassemble', '__init__.py')):
#    with open(os.path.join(PLAYGROUND_MODULES_DIRECTORY, 'docassemble', '__init__.py'), 'a') as the_file:
#        the_file.write(init_py_file)

#USE_PROGRESS_BAR = daconfig.get('use_progress_bar', True)
SHOW_LOGIN = daconfig.get('show_login', True)
#USER_PACKAGES = daconfig.get('user_packages', '/var/lib/docassemble/dist-packages')
#sys.path.append(USER_PACKAGES)
#if USE_PROGRESS_BAR:

if in_celery:
    LOGFILE = daconfig.get('celery_flask_log', '/tmp/celery-flask.log')
else:
    LOGFILE = daconfig.get('flask_log', '/tmp/flask.log')
#APACHE_LOGFILE = daconfig.get('apache_log', '/var/log/apache2/error.log')

connect_string = docassemble.webapp.database.connection_string()
alchemy_connect_string = docassemble.webapp.database.alchemy_connection_string()

def my_default_url(error, endpoint, values):
    return url_for('index')

app.handle_url_build_error = my_default_url

engine = create_engine(alchemy_connect_string, convert_unicode=True)
metadata = MetaData(bind=engine)
#store = SQLAlchemyStore(engine, metadata, 'kvstore')

redis_host = daconfig.get('redis', None)
if redis_host is None:
    redis_host = 'redis://localhost'

docassemble.base.util.set_redis_server(redis_host)

store = RedisStore(redis.StrictRedis(host=docassemble.base.util.redis_server, db=1))

kv_session = KVSessionExtension(store, app)

def get_url_from_file_reference(file_reference, **kwargs):
    file_reference = str(file_reference)
    if re.search(r'^http', file_reference):
        return(file_reference)
    if file_reference in ['login', 'signin']:
        return(url_for('user.login', **kwargs))
    elif file_reference == 'interviews':
        return(url_for('interview_list', **kwargs))
    elif file_reference == 'playground':
        return(url_for('playground_page', **kwargs))
    elif file_reference == 'playgroundtemplate':
        return(url_for('playground_files', section='template'))
    elif file_reference == 'playgroundstatic':
        return(url_for('playground_files', section='static'))
    elif file_reference == 'playgroundsources':
        return(url_for('playground_files', section='sources'))
    elif file_reference == 'playgroundmodules':
        return(url_for('playground_files', section='modules'))
    elif file_reference == 'playgroundpackages':
        return(url_for('playground_packages', **kwargs))
    elif file_reference == 'playgroundfiles':
        return(url_for('playground_files', **kwargs))
    elif file_reference == 'create_playground_package':
        return(url_for('create_playground_package', **kwargs))
    if re.match('[0-9]+', file_reference):
        file_number = file_reference
        if can_access_file_number(file_number):
            the_file = SavedFile(file_number)
            url = the_file.url_for(**kwargs)
        else:
            url = 'about:blank'
    else:
        question = kwargs.get('question', None)
        root = daconfig.get('root', '/')
        fileroot = daconfig.get('fileserver', root)
        if 'ext' in kwargs:
            extn = kwargs['ext']
            extn = re.sub(r'^\.', '', extn)
            extn = '.' + extn
        else:
            extn = ''
        parts = file_reference.split(':')
        if len(parts) < 2:
            file_reference = re.sub(r'^data/static/', '', file_reference)
            the_package = None
            if question is not None:
                the_package = question.from_source.package
            if the_package is None:
                the_package = 'docassemble.base'
            parts = [the_package, file_reference]
            #the_file = None
            #try:
            #the_file = pkg_resources.resource_filename(pkg_resources.Requirement.parse(parts[0]), re.sub(r'\.', r'/', parts[0]) + '/' + parts[1])
            #except:
            #    if current_user.is_authenticated and not current_user.is_anonymous:
            #        return(fileroot + "playgroundstatic/" + file_reference)
            #if not os.path.isfile(the_file) and current_user.is_authenticated and not current_user.is_anonymous:
            #    return(fileroot + "playgroundstatic/" + file_reference)
        parts[1] = re.sub(r'^data/static/', '', parts[1])
        url = fileroot + 'packagestatic/' + parts[0] + '/' + parts[1] + extn
    return(url)

class FakeUser(object):
    pass
class FakeRole(object):
    pass
def user_id_dict():
    output = dict()
    for user in User.query.all():
        output[user.id] = user
    anon = FakeUser()
    anon_role = FakeRole()
    anon_role.name = word('anonymous')
    anon.roles = [anon_role]
    anon.id = -1
    anon.firstname = 'Anonymous'
    anon.lastname = 'User'
    output[-1] = anon
    return output

docassemble.base.util.set_user_id_function(user_id_dict)

docassemble.base.parse.set_url_finder(get_url_from_file_reference)

def get_documentation_dict():
    documentation = get_info_from_file_reference('docassemble.base:data/questions/documentation.yml')
    if 'fullpath' in documentation and documentation['fullpath'] is not None:
        with open(documentation['fullpath'], 'rU') as fp:
            content = fp.read().decode('utf8')
            content = fix_tabs.sub('  ', content)
            return(yaml.load(content))
    return(None)

def get_name_info():
    docstring = get_info_from_file_reference('docassemble.base:data/questions/docstring.yml')
    if 'fullpath' in docstring and docstring['fullpath'] is not None:
        with open(docstring['fullpath'], 'rU') as fp:
            content = fp.read().decode('utf8')
            content = fix_tabs.sub('  ', content)
            return(yaml.load(content))
    return(None)

def get_title_documentation():
    documentation = get_info_from_file_reference('docassemble.base:data/questions/title_documentation.yml')
    if 'fullpath' in documentation and documentation['fullpath'] is not None:
        with open(documentation['fullpath'], 'rU') as fp:
            content = fp.read().decode('utf8')
            content = fix_tabs.sub('  ', content)
            return(yaml.load(content))
    return(None)

title_documentation = get_title_documentation()
documentation_dict = get_documentation_dict()
base_name_info = get_name_info()
for val in base_name_info:
    base_name_info[val]['name'] = val
    base_name_info[val]['insert'] = val
    if 'show' not in base_name_info[val]:
        base_name_info[val]['show'] = False

key_requires_preassembly = re.compile('^(x\.|x\[|_multiple_choice)')
match_invalid = re.compile('[^A-Za-z0-9_\[\].\'\%\-=]')
match_invalid_key = re.compile('[^A-Za-z0-9_\[\].\'\%\- =]')
match_brackets = re.compile('\[\'.*\'\]$')
match_inside_and_outside_brackets = re.compile('(.*)(\[\'[^\]]+\'\])$')
match_inside_brackets = re.compile('\[\'([^\]]+)\'\]')

if 'twilio' in daconfig:
    twilio_config = dict()
    twilio_config['account sid'] = dict()
    twilio_config['number'] = dict()
    twilio_config['name'] = dict()
    if type(daconfig['twilio']) is not list:
        config_list = [daconfig['twilio']]
    else:
        config_list = daconfig['twilio']
    for tconfig in config_list:
        if type(tconfig) is dict and 'account_sid' in tconfig and 'number' in tconfig:
            twilio_config['account sid'][tconfig['account sid']] = 1
            twilio_config['number'] = tconfig
            if 'default' not in twilio_config['name']:
                twilio_config['name']['default'] = tconfig
            if 'name' in tconfig:
                twilio_config['name'][tconfig['name']] = tconfig
    if 'default' not in twilio_config['name']:
        twilio_config = None
else:
    twilio_config = None

APPLICATION_NAME = 'docassemble'
app.config['USE_GOOGLE_LOGIN'] = False
app.config['USE_FACEBOOK_LOGIN'] = False
if 'oauth' in daconfig:
    app.config['OAUTH_CREDENTIALS'] = daconfig['oauth']
    if 'google' in daconfig['oauth'] and not ('enable' in daconfig['oauth']['google'] and daconfig['oauth']['google']['enable'] is False):
        app.config['USE_GOOGLE_LOGIN'] = True
    if 'facebook' in daconfig['oauth'] and not ('enable' in daconfig['oauth']['facebook'] and daconfig['oauth']['facebook']['enable'] is False):
        app.config['USE_FACEBOOK_LOGIN'] = True

password_secret_key = daconfig.get('password_secretkey', app.secret_key)
#app.secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits)
#                         for x in xrange(32))

word_file_list = daconfig.get('words', list())
if type(word_file_list) is not list:
    word_file_list = [word_file_list]
for word_file in word_file_list:
    sys.stderr.write("Reading from " + str(word_file) + "\n")
    file_info = get_info_from_file_reference(word_file)
    if 'fullpath' in file_info and file_info['fullpath'] is not None:
        with open(file_info['fullpath'], 'rU') as stream:
            for document in yaml.load_all(stream):
                if document and type(document) is dict:
                    for lang, words in document.iteritems():
                        if type(words) is dict:
                            docassemble.base.functions.update_word_collection(lang, words)
                        else:
                            sys.stderr.write("Error reading " + str(word_file) + ": words not in dictionary form.\n")
                else:
                    sys.stderr.write("Error reading " + str(word_file) + ": yaml file not in dictionary form.\n")
    else:
        sys.stderr.write("Error reading " + str(word_file) + ": yaml file not found.\n")
        
def logout():
    secret = request.cookies.get('secret', None)
    if secret is None:
        secret = ''.join(random.choice(string.ascii_letters) for i in range(16))
        set_cookie = True
    else:
        set_cookie = False
    user_manager = current_app.user_manager
    flask_user.signals.user_logged_out.send(current_app._get_current_object(), user=current_user)
    logout_user()
    delete_session()
    flash(word('You have signed out successfully.'), 'success')
    next = request.args.get('next', _endpoint_url(user_manager.after_logout_endpoint))
    response = redirect(next)
    if set_cookie:
        response.set_cookie('secret', secret)
    return response

def _call_or_get(function_or_property):
    return function_or_property() if callable(function_or_property) else function_or_property

def pad_to_16(the_string):
    if len(the_string) >= 16:
        return the_string[:16]
    return str(the_string) + (16 - len(the_string)) * '0'

def decrypt_session(secret):
    nowtime = datetime.datetime.utcnow()
    user_code = session.get('uid', None)
    filename = session.get('i', None)
    if user_code == None or filename == None or secret is None:
        return
    changed = False
    for record in SpeakList.query.filter_by(key=user_code, filename=filename, encrypted=True).all():
        phrase = decrypt_phrase(record.phrase, secret)
        record.phrase = pack_phrase(phrase)
        record.encrypted = False
        changed = True
    if changed:
        db.session.commit()
    changed = False
    for record in Attachments.query.filter_by(key=user_code, filename=filename, encrypted=True).all():
        if record.dictionary:
            the_dict = decrypt_dictionary(record.dictionary, secret)
            record.dictionary = pack_dictionary(the_dict)
            record.encrypted = False
            record.modtime = nowtime
            changed = True
    if changed:
        db.session.commit()
    changed = False
    for record in UserDict.query.filter_by(key=user_code, filename=filename, encrypted=True).order_by(UserDict.indexno).all():
        the_dict = decrypt_dictionary(record.dictionary, secret)
        record.dictionary = pack_dictionary(the_dict)
        record.encrypted = False
        record.modtime = nowtime
        changed = True
    if changed:
        db.session.commit()
    changed = False
    for record in ChatLog.query.filter_by(key=user_code, filename=filename, encrypted=True).all():
        phrase = decrypt_phrase(record.message, secret)
        record.message = pack_phrase(phrase)
        record.encrypted = False
        changed = True
    if changed:
        db.session.commit()
    return

def encrypt_session(secret):
    nowtime = datetime.datetime.utcnow()
    user_code = session.get('uid', None)
    filename = session.get('i', None)
    if user_code == None or filename == None or secret is None:
        return
    changed = False
    for record in SpeakList.query.filter_by(key=user_code, filename=filename, encrypted=False).all():
        phrase = unpack_phrase(record.phrase)
        record.phrase = encrypt_phrase(phrase, secret)
        record.encrypted = True
        changed = True
    if changed:
        db.session.commit()
    changed = False
    for record in Attachments.query.filter_by(key=user_code, filename=filename, encrypted=False).all():
        if record.dictionary:
            the_dict = unpack_dictionary(record.dictionary)
            record.dictionary = encrypt_dictionary(the_dict, secret)
            record.encrypted = True
            record.modtime = nowtime
            changed = True
    if changed:
        db.session.commit()
    changed = False
    for record in UserDict.query.filter_by(key=user_code, filename=filename, encrypted=False).order_by(UserDict.indexno).all():
        the_dict = unpack_dictionary(record.dictionary)
        record.dictionary = encrypt_dictionary(the_dict, secret)
        record.encrypted = True
        record.modtime = nowtime
        changed = True
    if changed:
        db.session.commit()
    changed = False
    for record in ChatLog.query.filter_by(key=user_code, filename=filename, encrypted=False).all():
        phrase = unpack_phrase(record.message)
        record.message = encrypt_phrase(phrase, secret)
        record.encrypted = True
        changed = True
    if changed:
        db.session.commit()
    return

def substitute_secret(oldsecret, newsecret):
    if oldsecret == None or oldsecret == newsecret:
        return newsecret
    user_code = session.get('uid', None)
    filename = session.get('i', None)
    if user_code == None or filename == None:
        return newsecret
    # currentsecret = None
    changed = False
    for record in SpeakList.query.filter_by(key=user_code, filename=filename).all():
        if record.encrypted:
            phrase = decrypt_phrase(record.phrase, oldsecret)
        else:
            phrase = unpack_phrase(record.phrase)
            record.encrypted = True
        record.phrase = encrypt_phrase(phrase, newsecret)
        changed = True
    if changed:
        db.session.commit()
    changed = False
    for record in Attachments.query.filter_by(key=user_code, filename=filename).all():
        if record.dictionary:
            #logmessage("Found old dictionary in attachments")
            if record.encrypted:
                the_dict = decrypt_dictionary(record.dictionary, oldsecret)
                #logmessage("Decrypted it with old secret " + oldsecret)
            else:
                the_dict = unpack_dictionary(record.dictionary)
                record.encrypted = True
            #logmessage("re-encrypted with secret " + newsecret)
            record.dictionary = encrypt_dictionary(the_dict, newsecret)
            changed = True
    if changed:
        db.session.commit()
    changed = False
    for record in UserDict.query.filter_by(key=user_code, filename=filename).order_by(UserDict.indexno).all():
        #logmessage("Found old dictionary in userdict")
        if record.encrypted:
            the_dict = decrypt_dictionary(record.dictionary, oldsecret)
            #logmessage("Decrypted it with old secret " + oldsecret)
        else:
            the_dict = unpack_dictionary(record.dictionary)
            record.encrypted = True
        record.dictionary = encrypt_dictionary(the_dict, newsecret)
        #logmessage("re-encrypted with secret " + newsecret)
        changed = True
    if changed:
        db.session.commit()
    changed = False
    for record in ChatLog.query.filter_by(key=user_code, filename=filename).all():
        if record.encrypted:
            phrase = decrypt_phrase(record.message, oldsecret)
        else:
            phrase = unpack_phrase(record.message)
            record.encrypted = True
        record.message = encrypt_phrase(phrase, newsecret)
        changed = True
    if changed:
        db.session.commit()
    return newsecret

def _do_login_user(user, password, secret, next, remember_me=False):
    # User must have been authenticated
    if not user:
        return unauthenticated()

    # Check if user account has been disabled
    if not _call_or_get(user.is_active):
        flash(word('Your account has not been enabled.'), 'error')
        return redirect(url_for('user.login'))

    # Check if user has a confirmed email address
    user_manager = current_app.user_manager
    if user_manager.enable_email and user_manager.enable_confirm_email \
            and not current_app.user_manager.enable_login_without_confirm_email \
            and not user.has_confirmed_email():
        url = url_for('user.resend_confirm_email')
        flash('Your email address has not yet been confirmed. Check your email Inbox and Spam folders for the confirmation email or <a href="' + str(url) + '">Re-send confirmation email</a>.', 'error')
        return redirect(url_for('user.login'))

    # Use Flask-Login to sign in user
    #print('login_user: remember_me=', remember_me)
    login_user(user, remember=remember_me)

    if 'i' in session and 'uid' in session:
        save_user_dict_key(session['uid'], session['i'])
        session['key_logged'] = True 

    # Send user_logged_in signal
    signals.user_logged_in.send(current_app._get_current_object(), user=user)

    if 'tempuser' in session:
        changed = False
        for chat_entry in ChatLog.query.filter_by(temp_user_id=int(session['tempuser'])).all():
            chat_entry.user_id = user.id
            chat_entry.temp_user_id = None
            changed = True
        if changed:
            db.session.commit()
        changed = False
        for chat_entry in ChatLog.query.filter_by(temp_owner_id=int(session['tempuser'])).all():
            chat_entry.owner_id = user.id
            chat_entry.temp_owner_id = None
            changed = True
        if changed:
            db.session.commit()
        del session['tempuser']
    session['user_id'] = user.id
    # Prepare one-time system message
    flash(word('You have signed in successfully.'), 'success')

    newsecret = substitute_secret(secret, pad_to_16(MD5.MD5Hash(data=password).hexdigest()))
    # Redirect to 'next' URL
    response = redirect(next)
    response.set_cookie('secret', newsecret)
    return response

def _endpoint_url(endpoint):
    url = '/'
    if endpoint:
        url = url_for(endpoint)
    return url

def custom_login():
    #logmessage("Got to login page")
    user_manager =  current_app.user_manager
    db_adapter = user_manager.db_adapter
    secret = request.cookies.get('secret', None)
    #logmessage("custom_login: secret is " + str(secret))
    next = request.args.get('next', _endpoint_url(user_manager.after_login_endpoint))
    reg_next = request.args.get('reg_next', _endpoint_url(user_manager.after_register_endpoint))

    # Immediately redirect already logged in users
    if _call_or_get(current_user.is_authenticated) and user_manager.auto_login_at_login:
        return redirect(next)

    # Initialize form
    login_form = user_manager.login_form(request.form)          # for login.html
    register_form = user_manager.register_form()                # for login_or_register.html
    if request.method != 'POST':
        login_form.next.data     = register_form.next.data = next
        login_form.reg_next.data = register_form.reg_next.data = reg_next

    # Process valid POST
    if request.method == 'POST':
        try:
            login_form.validate()
        except:
            logmessage("Got an error when validating login")
            pass
    if request.method == 'POST' and login_form.validate():
        # Retrieve User
        user = None
        user_email = None
        if user_manager.enable_username:
            # Find user record by username
            user = user_manager.find_user_by_username(login_form.username.data)
            user_email = None
            # Find primary user_email record
            if user and db_adapter.UserEmailClass:
                user_email = db_adapter.find_first_object(db_adapter.UserEmailClass,
                        user_id=int(user.get_id()),
                        is_primary=True,
                        )
            # Find user record by email (with form.username)
            if not user and user_manager.enable_email:
                user, user_email = user_manager.find_user_by_email(login_form.username.data)
        else:
            # Find user by email (with form.email)
            user, user_email = user_manager.find_user_by_email(login_form.email.data)

        if user:
            # Log user in
            return _do_login_user(user, login_form.password.data, secret, login_form.next.data, login_form.remember_me.data)

    # Process GET or invalid POST
    return render_template(user_manager.login_template,
            form=login_form,
            login_form=login_form,
            register_form=register_form)

def setup_app(app, db):
    from docassemble.webapp.users.forms import MyRegisterForm
    from docassemble.webapp.users.views import user_profile_page
    #from docassemble.webapp.users import models
    #from docassemble.webapp.pages import views
    #from docassemble.webapp.users import views
    db_adapter = SQLAlchemyAdapter(db, User, UserAuthClass=UserAuth)
    user_manager = UserManager(db_adapter, app, register_form=MyRegisterForm, user_profile_view_function=user_profile_page, logout_view_function=logout, login_view_function=custom_login)
    return(app)

setup_app(app, db)
lm = LoginManager(app)
lm.login_view = 'user.login'

supervisor_url = os.environ.get('SUPERVISOR_SERVER_URL', None)
if supervisor_url:
    USING_SUPERVISOR = True
    #sys.stderr.write("Using supervisor and hostname is " + str(hostname) + "\n")
else:
    USING_SUPERVISOR = False
    #sys.stderr.write("Not using supervisor and hostname is " + str(hostname) + "\n")

sys_logger = logging.getLogger('docassemble')
sys_logger.setLevel(logging.DEBUG)

if LOGSERVER is None:
    docassemble_log_handler = logging.FileHandler(filename=os.path.join(LOG_DIRECTORY, 'docassemble.log'))
    sys_logger.addHandler(docassemble_log_handler)
else:
    import logging.handlers
    handler = logging.handlers.SysLogHandler(address=(LOGSERVER, 514), socktype=socket.SOCK_STREAM)
    sys_logger.addHandler(handler)

request_active = True

def set_request_active(value):
    global request_active
    request_active = value

LOGFORMAT = 'docassemble: ip=%(clientip)s i=%(yamlfile)s uid=%(session)s user=%(user)s %(message)s'
def syslog_message(message):
    message = re.sub(r'\n', ' ', message)
    if current_user and current_user.is_authenticated and not current_user.is_anonymous:
        the_user = current_user.email
    else:
        the_user = "anonymous"
    if request_active:
        sys_logger.debug('%s', LOGFORMAT % {'message': message, 'clientip': request.remote_addr, 'yamlfile': session.get('i', 'na'), 'user': the_user, 'session': session.get('uid', 'na')})
    else:
        sys_logger.debug('%s', LOGFORMAT % {'message': message, 'clientip': 'localhost', 'yamlfile': 'na', 'user': 'na', 'session': 'na'})

def syslog_message_with_timestamp(message):
    syslog_message(time.strftime("%Y-%m-%d %H:%M:%S") + " " + message)
    
if LOGSERVER is None:
    docassemble.base.logger.set_logmessage(syslog_message_with_timestamp)
else:
    docassemble.base.logger.set_logmessage(syslog_message)

def copy_playground_modules():
    devs = list()
    for user in User.query.filter_by(active=True).all():
        for role in user.roles:
            if role.name == 'admin' or role.name == 'developer':
                devs.append(user.id)
    for user_id in devs:
        mod_dir = SavedFile(user_id, fix=True, section='playgroundmodules')
        local_dir = os.path.join(FULL_PACKAGE_DIRECTORY, 'docassemble', 'playground' + str(user_id))
        if os.path.isdir(local_dir):
            shutil.rmtree(local_dir)
        #sys.stderr.write("Copying " + str(mod_dir.directory) + " to " + str(local_dir) + "\n")
        shutil.copytree(mod_dir.directory, local_dir)
        with open(os.path.join(local_dir, '__init__.py'), 'a') as the_file:
            the_file.write(init_py_file)

copy_playground_modules()
#sys.path.append(PLAYGROUND_MODULES_DIRECTORY)

# END OF INITIALIZATION

def proc_example_list(example_list, examples):
    for example in example_list:
        if type(example) is dict:
            for key, value in example.iteritems():
                sublist = list()
                proc_example_list(value, sublist)
                examples.append({'title': str(key), 'list': sublist})
                break
            continue
        result = dict()
        result['id'] = example
        result['interview'] = url_for('index', i="docassemble.base:data/questions/examples/" + example + ".yml")
        example_file = 'docassemble.base:data/questions/examples/' + example + '.yml'
        result['image'] = url_for('static', filename='examples/' + example + ".png")
        file_info = get_info_from_file_reference(example_file)
        start_block = 1
        end_block = 2
        if 'fullpath' not in file_info or file_info['fullpath'] is None:
            continue
        try:
            interview = docassemble.base.interview_cache.get_interview(example_file)
            if len(interview.metadata):
                metadata = interview.metadata[0]
                result['title'] = metadata.get('title', metadata.get('short title', word('Untitled'))).rstrip()
                result['documentation'] = metadata.get('documentation', None)
                start_block = int(metadata.get('example start', 1))
                end_block = int(metadata.get('example end', start_block)) + 1
            else:
                continue
        except:
            continue
        with open(file_info['fullpath'], 'rU') as fp:
            content = fp.read().decode('utf8')
            content = fix_tabs.sub('  ', content)
            content = fix_initial.sub('', content)
            blocks = map(lambda x: x.strip(), document_match.split(content))
            if len(blocks):
                if re.search(r'metadata:', blocks[0]) and start_block > 0:
                    initial_block = 1
                else:
                    initial_block = 0
                if start_block > initial_block:
                    result['before_html'] = highlight("\n---\n".join(blocks[initial_block:start_block]) + "\n---", YamlLexer(), HtmlFormatter())
                else:
                    result['before_html'] = ''
                if len(blocks) > end_block:
                    result['after_html'] = highlight("---\n" + "\n---\n".join(blocks[end_block:len(blocks)]), YamlLexer(), HtmlFormatter())
                else:
                    result['after_html'] = ''
                result['source'] = "\n---\n".join(blocks[start_block:end_block])
                result['html'] = highlight(result['source'], YamlLexer(), HtmlFormatter())
        examples.append(result)
    
def get_examples():
    examples = list()
    example_list_file = get_info_from_file_reference('docassemble.base:data/questions/example-list.yml')
    if 'fullpath' in example_list_file and example_list_file['fullpath'] is not None:
        example_list = list()
        with open(example_list_file['fullpath'], 'rU') as fp:
            content = fp.read().decode('utf8')
            content = fix_tabs.sub('  ', content)
            proc_example_list(yaml.load(content), examples)
    #logmessage("Examples: " + str(examples))
    return(examples)

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

class OAuthSignIn(object):
    providers = None

    def __init__(self, provider_name):
        self.provider_name = provider_name
        credentials = current_app.config['OAUTH_CREDENTIALS'][provider_name]
        self.consumer_id = credentials['id']
        self.consumer_secret = credentials['secret']

    def authorize(self):
        pass

    def callback(self):
        pass

    def get_callback_url(self):
        return url_for('oauth_callback', provider=self.provider_name,
                       _external=True)

    @classmethod
    def get_provider(self, provider_name):
        if self.providers is None:
            self.providers = {}
            for provider_class in self.__subclasses__():
                provider = provider_class()
                self.providers[provider.provider_name] = provider
        return self.providers[provider_name]

class GoogleSignIn(OAuthSignIn):
    def __init__(self):
        super(GoogleSignIn, self).__init__('google')
        self.service = OAuth2Service(
            name='google',
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url=None,
            access_token_url=None,
            base_url=None
        )
    def authorize(self):
        result = urlparse.parse_qs(request.data)
        session['google_id'] = result.get('id', [None])[0]
        session['google_email'] = result.get('email', [None])[0]
        response = make_response(json.dumps('Successfully connected user.', 200))
        response.headers['Content-Type'] = 'application/json'
        return response
    
    def callback(self):
        email = session.get('google_email')
        return (
            'google$' + str(session.get('google_id')),
            email.split('@')[0],
            email
        )

class FacebookSignIn(OAuthSignIn):
    def __init__(self):
        super(FacebookSignIn, self).__init__('facebook')
        self.service = OAuth2Service(
            name='facebook',
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url='https://graph.facebook.com/oauth/authorize',           
            access_token_url='https://graph.facebook.com/oauth/access_token',
            base_url='https://graph.facebook.com/'
        )
    def authorize(self):
        return redirect(self.service.get_authorize_url(
            scope='email',
            response_type='code',
            redirect_uri=self.get_callback_url())
        )
    def callback(self):
        if 'code' not in request.args:
            return None, None, None
        oauth_session = self.service.get_auth_session(
            data={'code': request.args['code'],
                  'grant_type': 'authorization_code',
                  'redirect_uri': self.get_callback_url()}
        )
        me = oauth_session.get('me').json()
        return (
            'facebook$' + me['id'],
            me.get('email').split('@')[0],
            me.get('email')
        )

# class TwitterSignIn(OAuthSignIn):
#     def __init__(self):
#         super(TwitterSignIn, self).__init__('twitter')
#         self.service = OAuth1Service(
#             name='twitter',
#             consumer_key=self.consumer_id,
#             consumer_secret=self.consumer_secret,
#             request_token_url='https://api.twitter.com/oauth/request_token',
#             authorize_url='https://api.twitter.com/oauth/authorize',
#             access_token_url='https://api.twitter.com/oauth/access_token',
#             base_url='https://api.twitter.com/1.1/'
#         )
#     def authorize(self):
#         request_token = self.service.get_request_token(
#             params={'oauth_callback': self.get_callback_url()}
#         )
#         session['request_token'] = request_token
#         return redirect(self.service.get_authorize_url(request_token[0]))
#     def callback(self):
#         request_token = session.pop('request_token')
#         if 'oauth_verifier' not in request.args:
#             return None, None, None
#         oauth_session = self.service.get_auth_session(
#             request_token[0],
#             request_token[1],
#             data={'oauth_verifier': request.args['oauth_verifier']}
#         )
#         me = oauth_session.get('account/verify_credentials.json').json()
#         social_id = 'twitter$' + str(me.get('id'))
#         username = me.get('screen_name')
#         return social_id, username, None   # Twitter does not provide email

@app.route('/authorize/<provider>', methods=['POST', 'GET'])
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('interview_list'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()

@app.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('interview_list'))
    oauth = OAuthSignIn.get_provider(provider)
    social_id, username, email = oauth.callback()
    if social_id is None:
        flash(word('Authentication failed.'), 'error')
        return redirect(url_for('interview_list'))
    user = User.query.filter_by(social_id=social_id).first()
    if not user:
        user = User.query.filter_by(email=email).first()
    if not user:
        user = User(social_id=social_id, nickname=username, email=email, active=True)
        db.session.add(user)
        db.session.commit()
    login_user(user, remember=False)
    if 'i' in session and 'uid' in session:
        save_user_dict_key(session['uid'], session['i'])
        session['key_logged'] = True 
    secret = request.cookies.get('secret', None)
    newsecret = substitute_secret(secret, pad_to_16(MD5.MD5Hash(data=social_id+password_secret_key).hexdigest()))
    if not current_user.is_anonymous:
        #update_user_id(session['uid'])
        flash(word('Welcome!  You are logged in as ') + email, 'success')
    response = redirect(url_for('interview_list'))
    response.set_cookie('secret', newsecret)
    return response

# @app.route('/login')
# def login():
#     msg = Message("Test message",
#                   sender="Docassemble <no-reply@docassemble.org>",
#                   recipients=["jhpyle@gmail.com"])
#     msg.body = "Testing, testing"
#     msg.html = "<p>Testing, testing.  Someone used the login page.</p>"
#     mail.send(msg)
#     form = LoginForm()
#     return render_template('flask_user/login.html', form=form, login_form=form, title="Sign in")

@app.route('/user/google-sign-in')
def google_page():
    return render_template('flask_user/google_login.html', title="Sign in")

@app.route("/user/post-sign-in", methods=['GET'])
def post_sign_in():
    session_id = session.get('uid', None)
    return redirect(url_for('interview_list'))

@app.route("/exit", methods=['POST', 'GET'])
def exit():
    session_id = session.get('uid', None)
    yaml_filename = session.get('i', None)
    if 'key_logged' in session:
        del session['key_logged']
    if session_id is not None and yaml_filename is not None:
        manual_checkout()
        obtain_lock(session_id, yaml_filename)
        reset_user_dict(session_id, yaml_filename)
        release_lock(session_id, yaml_filename)
    return redirect(exit_page)

@app.route("/cleanup_sessions", methods=['GET'])
def cleanup_sessions():
    kv_session.cleanup_sessions()
    return render_template('base_templates/blank.html')

def add_timestamps(the_dict, manual_user_id=None):
    nowtime = datetime.datetime.utcnow()
    the_dict['_internal']['starttime'] = nowtime 
    the_dict['_internal']['modtime'] = nowtime
    if manual_user_id is not None or (current_user and current_user.is_authenticated and not current_user.is_anonymous):
        if manual_user_id is not None:
            the_user_id = manual_user_id
        else:
            the_user_id = current_user.id
        the_dict['_internal']['accesstime'][the_user_id] = nowtime
    else:
        the_dict['_internal']['accesstime'][-1] = nowtime
    return

def fresh_dictionary():
    the_dict = copy.deepcopy(initial_dict)
    add_timestamps(the_dict)
    return the_dict    

def manual_checkout():
    session_id = session.get('uid', None)
    yaml_filename = session.get('i', None)
    if session_id is None or yaml_filename is None:
        return
    if current_user.is_anonymous:
        the_user_id = 't' + str(session.get('tempuser', None))
    else:
        the_user_id = current_user.id
    endpart = ':uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:' + str(the_user_id)
    #logmessage("Checking out from " + endpart)
    pipe = r.pipeline()
    pipe.expire('da:session' + endpart, 12)
    pipe.expire('da:html' + endpart, 12)
    pipe.expire('da:chatsession' + endpart, 12)
    pipe.expire('da:ready' + endpart, 12)
    pipe.expire('da:block' + endpart, 12)
    pipe.execute()
    #r.publish('da:monitor', json.dumps(dict(messagetype='refreshsessions')))
    #logmessage("Done checking out from " + endpart)
    return

@app.route("/checkout", methods=['POST', 'GET'])
def checkout():
    try:
        manual_checkout()
    except:
        return jsonify(success=False)
    return jsonify(success=True)

@app.route("/restart_ajax", methods=['POST'])
@login_required
@roles_required(['admin', 'developer'])
def restart_ajax():
    logmessage("Action is " + str(request.form.get('action', None)))
    # if 'restart' in session:
    #     logmessage("Restart is in session")
    # else:
    #     logmessage("Restart is not in session")
    if current_user.has_role('admin', 'developer'):
        logmessage("User has perms")
    else:
        logmessage("User has no perms")
    if request.form.get('action', None) == 'restart' and current_user.has_role('admin', 'developer'):
        #del session['restart']
        restart_all()
        return jsonify(success=True)

class ChatPartners(object):
    pass
    
def chat_partners_available(session_id, yaml_filename, the_user_id, mode, partner_roles):
    key = 'da:session:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:' + str(the_user_id)
    if mode in ['peer', 'peerhelp']:
        peer_ok = True
    else:
        peer_ok = False
    if mode in ['help', 'peerhelp']:
        help_ok = True
    else:
        help_ok = False
    potential_partners = set()
    if help_ok and len(partner_roles) and not r.exists('da:block:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:' + str(the_user_id)):
        chat_session_key = 'da:chatsession:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:' + str(the_user_id)
        for role in partner_roles:
            for the_key in r.keys('da:monitor:role:' + role + ':userid:*'):
                user_id = re.sub(r'^.*:userid:', '', the_key)
                potential_partners.add(user_id)
        for the_key in r.keys('da:monitor:chatpartners:*'):
            user_id = re.sub(r'^.*chatpartners:', '', the_key)
            if user_id not in potential_partners:
                for chat_key in r.hgetall(the_key):
                    if chat_key == chat_session_key:
                        potential_partners.add(user_id)
    num_peer = 0
    if peer_ok:
        for sess_key in r.keys('da:session:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:*'):
            if sess_key != key:
                num_peer += 1
    result = ChatPartners()
    result.peer = num_peer
    result.help = len(potential_partners)
    #return (dict(peer=num_peer, help=len(potential_partners)))
    return result
    
@app.route("/checkin", methods=['POST', 'GET'])
def checkin():
    session_id = session.get('uid', None)
    yaml_filename = session.get('i', None)
    if 'visitor_secret' in request.cookies:
        secret = request.cookies['visitor_secret']
    else:
        secret = request.cookies.get('secret', None)
    #session_cookie_id = request.cookies.get('session', None)
    if session_id is None or yaml_filename is None:
        return jsonify(success=False)
    if current_user.is_anonymous:
        the_user_id = 't' + str(session['tempuser'])
        auth_user_id = None
        temp_user_id = int(session['tempuser'])
    else:
        auth_user_id = current_user.id
        the_user_id = current_user.id
        temp_user_id = None
    if request.form.get('action', None) == 'chat_log':
        steps, user_dict, is_encrypted = fetch_user_dict(session_id, yaml_filename, secret=secret)
        if user_dict['_internal']['chat']['availability'] == 'unavailable':
            return jsonify(success=False)
        messages = get_chat_log(user_dict['_internal']['chat']['mode'], yaml_filename, session_id, auth_user_id, temp_user_id, secret, auth_user_id, temp_user_id)
        return jsonify(success=True, messages=messages)
    if request.form.get('action', None) == 'checkin':
        #logmessage("Doing redis statement")
        peer_ok = False
        help_ok = False
        num_peers = 0
        help_available = 0
        old_chatstatus = session.get('chatstatus', None)
        chatstatus = request.form.get('chatstatus', 'off')
        if old_chatstatus != chatstatus:
            session['chatstatus'] = chatstatus
        obj = dict(chatstatus=chatstatus, i=yaml_filename, uid=session_id, userid=the_user_id)
        key = 'da:session:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:' + str(the_user_id)
        call_forwarding_on = False
        forwarding_phone_number = None
        if twilio_config is not None:
            forwarding_phone_number = twilio_config['name']['default'].get('number', None)
            if forwarding_phone_number is not None:
                call_forwarding_on = True
        call_forwarding_code = None
        call_forwarding_message = None
        if call_forwarding_on:
            for call_key in r.keys(re.sub(r'^da:session:uid:', 'da:phonecode:monitor:*:uid:', key)):
                call_forwarding_code = r.get(call_key)
                if call_forwarding_code is not None:
                    other_value = r.get('da:callforward:' + str(call_forwarding_code))
                    if other_value is None:
                        r.delete(call_key)
                        continue
                    remaining_seconds = r.ttl(call_key)
                    if remaining_seconds > 30:
                        call_forwarding_message = '<span class="phone-message"><i class="glyphicon glyphicon-earphone"></i> ' + word('To reach an advocate who can assist you, call') + ' <a class="phone-number" href="tel:' + str(forwarding_phone_number) + '">' + str(forwarding_phone_number) + '</a> ' + word("and enter the code") + ' <span class="phone-code">' + str(call_forwarding_code) + '</span>.</span>'
                        break
        chat_session_key = 'da:chatsession:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:' + str(the_user_id)
        potential_partners = list()
        if str(chatstatus) in ['waiting', 'standby', 'ringing', 'ready', 'on', 'hangup']:
            steps, user_dict, is_encrypted = fetch_user_dict(session_id, yaml_filename, secret=secret)
            obj['secret'] = secret
            obj['encrypted'] = is_encrypted
            obj['roles'] = user_dict['_internal']['chat']['roles']
            obj['mode'] = user_dict['_internal']['chat']['mode']
            if obj['mode'] in ['peer', 'peerhelp']:
                peer_ok = True
            if obj['mode'] in ['help', 'peerhelp']:
                help_ok = True
            obj['partner_roles'] = user_dict['_internal']['chat']['partner_roles']
            if current_user.is_authenticated:
                for attribute in ['email', 'confirmed_at', 'first_name', 'last_name', 'country', 'subdivisionfirst', 'subdivisionsecond', 'subdivisionthird', 'organization', 'timezone']:
                    obj[attribute] = getattr(current_user, attribute, None)
            else:
                obj['temp_user_id'] = temp_user_id
            if help_ok and len(obj['partner_roles']) and not r.exists('da:block:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:' + str(the_user_id)):
                pipe = r.pipeline()
                for role in obj['partner_roles']:
                    role_key = 'da:chat:roletype:' + str(role)
                    pipe.set(role_key, 1)
                    pipe.expire(role_key, 2592000)
                pipe.execute()
                for role in obj['partner_roles']:
                    for the_key in r.keys('da:monitor:role:' + role + ':userid:*'):
                        user_id = re.sub(r'^.*:userid:', '', the_key)
                        if user_id not in potential_partners:
                            potential_partners.append(user_id)
                for the_key in r.keys('da:monitor:chatpartners:*'):
                    user_id = re.sub(r'^.*chatpartners:', '', the_key)
                    if user_id not in potential_partners:
                        for chat_key in r.hgetall(the_key):
                            if chat_key == chat_session_key:
                                potential_partners.append(user_id)
            if len(potential_partners) > 0:
                if chatstatus == 'ringing':
                    lkey = 'da:ready:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:' + str(the_user_id)
                    #logmessage("Writing to " + str(lkey))
                    pipe = r.pipeline()
                    failure = True
                    for user_id in potential_partners:
                        for the_key in r.keys('da:monitor:available:' + str(user_id)):
                            pipe.rpush(lkey, the_key)
                            failure = False
                    if peer_ok:
                        for the_key in r.keys('da:chatsession:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:*'):
                            if the_key != chat_session_key:
                                pipe.rpush(lkey, the_key)
                                failure = False
                    if failure:
                        if peer_ok:
                            chatstatus = 'ready'
                        else:
                            chatstatus = 'waiting'
                        session['chatstatus'] = chatstatus
                        obj['chatstatus'] = chatstatus
                    else:
                        pipe.expire(lkey, 60)
                        pipe.execute()
                        #logmessage("Wrote to " + str(lkey))
                        chatstatus = 'ready'
                        session['chatstatus'] = chatstatus
                        obj['chatstatus'] = chatstatus
                elif chatstatus in ['on']:
                    if len(potential_partners) > 0:
                        already_connected_to_help = False
                        current_helper = None
                        for user_id in potential_partners:
                            for the_key in r.hgetall('da:monitor:chatpartners:' + str(user_id)):
                                if the_key == chat_session_key:
                                    already_connected_to_help = True
                                    current_helper = user_id
                        if not already_connected_to_help:
                            for user_id in potential_partners:
                                mon_sid = r.get('da:monitor:available:' + str(user_id))
                                if mon_sid is None:
                                    continue
                                int_sid = r.get('da:chatsession:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:' + str(the_user_id))
                                if int_sid is None:
                                    continue
                                r.publish(mon_sid, json.dumps(dict(messagetype='chatready', uid=session_id, i=yaml_filename, userid=the_user_id, secret=secret, sid=int_sid)))
                                r.publish(int_sid, json.dumps(dict(messagetype='chatpartner', sid=mon_sid)))
                                break
                if chatstatus in ['waiting', 'hangup']:
                    chatstatus = 'standby'
                    session['chatstatus'] = chatstatus
                    obj['chatstatus'] = chatstatus
            else:
                #logmessage("Peer ok is " + str(peer_ok) + " and chatstatus is " + str(chatstatus))
                if peer_ok:
                    if chatstatus == 'ringing':
                        lkey = 'da:ready:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:' + str(the_user_id)
                        #logmessage("Writing to " + str(lkey))
                        pipe = r.pipeline()
                        failure = True
                        for the_key in r.keys('da:chatsession:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:*'):
                            if the_key != chat_session_key:
                                pipe.rpush(lkey, the_key)
                                failure = False
                        if not failure:
                            pipe.expire(lkey, 6000)
                            pipe.execute()
                            #logmessage("Wrote to " + str(lkey))
                        chatstatus = 'ready'
                        session['chatstatus'] = chatstatus
                        obj['chatstatus'] = chatstatus
                    elif chatstatus in ['waiting', 'hangup']:
                        chatstatus = 'standby'
                        session['chatstatus'] = chatstatus
                        obj['chatstatus'] = chatstatus
                else:
                    if chatstatus in ['standby', 'ready', 'ringing', 'hangup']:
                        chatstatus = 'waiting'
                        session['chatstatus'] = chatstatus
                        obj['chatstatus'] = chatstatus
            if peer_ok:
                for sess_key in r.keys('da:session:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:*'):
                    if sess_key != key:
                        num_peers += 1
        help_available = len(potential_partners)
        html_key = 'da:html:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:' + str(the_user_id)
        if old_chatstatus != chatstatus:
            #logmessage("Doing a sessionupdate because " + str(chatstatus))
            html = r.get(html_key)
            if html is not None:
                html_obj = json.loads(html)
                if 'browser_title' in html_obj:
                    obj['browser_title'] = html_obj['browser_title']
                if r.exists('da:block:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:' + str(the_user_id)):
                    obj['blocked'] = True
                else:
                    obj['blocked'] = False
                r.publish('da:monitor', json.dumps(dict(messagetype='sessionupdate', key=key, session=obj)))
            else:
                logmessage("The html was not found")
        #logmessage("Setting " + key)
        pipe = r.pipeline()
        pipe.set(key, pickle.dumps(obj))
        pipe.expire(key, 60)
        pipe.expire(html_key, 60)
        pipe.execute()
        #logmessage("Done setting " + key)
        parameters = request.form.get('parameters', None)
        if parameters is not None:
            key = 'da:input:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:' + str(the_user_id)
            r.publish(key, parameters)
        if peer_ok or help_ok:
            return jsonify(success=True, chat_status=chatstatus, num_peers=num_peers, help_available=help_available, phone=call_forwarding_message)
        else:
            return jsonify(success=True, chat_status=chatstatus, phone=call_forwarding_message)
    return jsonify(success=False)

def do_redirect(url, is_ajax):
    if is_ajax:
        return jsonify(action='redirect', url=url)
    else:
        return redirect(url)

def standard_scripts():
    return '\n    <script src="' + url_for('static', filename='app/jquery.min.js') + '"></script>\n    <script src="' + url_for('static', filename='app/jquery.validate.min.js') + '"></script>\n    <script src="' + url_for('static', filename='bootstrap/js/bootstrap.min.js') + '"></script>\n    <script src="' + url_for('static', filename='app/jasny-bootstrap.min.js') + '"></script>\n    <script src="' + url_for('static', filename='bootstrap-slider/bootstrap-slider.min.js') + '"></script>\n    <script src="' + url_for('static', filename='bootstrap-fileinput/js/fileinput.min.js') + '"></script>\n    <script src="' + url_for('static', filename='app/signature.js') + '"></script>\n    <script src="' + url_for('static', filename='app/socket.io.min.js') + '"></script>\n    <script src="' + url_for('static', filename='jquery-labelauty/source/jquery-labelauty.js') + '"></script>\n'
    
def standard_html_start(interview_language=DEFAULT_LANGUAGE, reload_after='', debug=False):
    output = '<!DOCTYPE html>\n<html lang="' + interview_language + '">\n  <head>\n    <meta charset="utf-8">\n    <meta name="mobile-web-app-capable" content="yes">\n    <meta name="apple-mobile-web-app-capable" content="yes">\n    <meta http-equiv="X-UA-Compatible" content="IE=edge">\n    <meta name="viewport" content="width=device-width, initial-scale=1">' + reload_after + '\n    <link href="' + url_for('static', filename='bootstrap/css/bootstrap.min.css') + '" rel="stylesheet">\n    <link href="' + url_for('static', filename='bootstrap/css/bootstrap-theme.min.css') + '" rel="stylesheet">\n    <link href="' + url_for('static', filename='app/jasny-bootstrap.min.css') + '" rel="stylesheet">\n    <link href="' + url_for('static', filename='bootstrap-fileinput/css/fileinput.min.css') + '" media="all" rel="stylesheet" type="text/css" />\n    <link href="' + url_for('static', filename='jquery-labelauty/source/jquery-labelauty.css') + '" rel="stylesheet">\n    <link href="' + url_for('static', filename='bootstrap-slider/css/bootstrap-slider.min.css') + '" rel="stylesheet">\n    <link href="' + url_for('static', filename='app/app.css') + '" rel="stylesheet">\n    <link href="' + url_for('static', filename='app/signature.css') + '" rel="stylesheet">'
    if debug:
        output += '\n    <link href="' + url_for('static', filename='app/pygments.css') + '" rel="stylesheet">'
    return output

# @app.before_request
# def before_request():
#     g.request_start_time = time.time()
#     g.request_time = lambda: "%.5fs" % (time.time() - g.request_start_time)

@app.route("/", methods=['POST', 'GET'])
def index():
    #seq = Sequence(message_sequence)
    #nextid = connection.execute(seq)
    if 'ajax' in request.form:
        #sys.stderr.write("This is ajax!\n")
        is_ajax = True
    else:
        is_ajax = False
    chatstatus = session.get('chatstatus', 'off')
    session_id = session.get('uid', None)
    if current_user.is_anonymous:
        if 'tempuser' not in session:
            new_temp_user = TempUser()
            db.session.add(new_temp_user)
            db.session.commit()
            session['tempuser'] = new_temp_user.id
    else:
        if 'user_id' not in session:
            session['user_id'] = current_user.id
    expire_visitor_secret = False
    if 'visitor_secret' in request.cookies:
        if 'session' in request.args:
            secret = request.cookies.get('secret', None)
            expire_visitor_secret = True
        else:
            secret = request.cookies['visitor_secret']
    else:
        secret = request.cookies.get('secret', None)
    encrypted = session.get('encrypted', True)
    if secret is None:
        secret = ''.join(random.choice(string.ascii_letters) for i in range(16))
        set_cookie = True
    else:
        set_cookie = False
    yaml_filename = session.get('i', default_yaml_filename)
    steps = 0
    need_to_reset = False
    # secret_parameter = request.args.get('sid', None)
    yaml_parameter = request.args.get('i', None)
    session_parameter = request.args.get('session', None)
    # if secret_parameter is not None:
    #     if currentsecret != secret_parameter:
    #         currentsecret = secret_parameter
    #         session['currentsecret'] = currentsecret
    if yaml_parameter is not None:
        show_flash = False
        yaml_filename = yaml_parameter
        # if session.get('nocache', False):
        #     docassemble.base.interview_cache.clear_cache(yaml_filename)
        old_yaml_filename = session.get('i', None)
        # if yaml_filename.startswith("/playground") and not current_user.is_authenticated:
        #     flash(word("You must be logged in as a developer to continue"), 'error')
        #     return redirect(url_for('user.login', next=url_for('index', **request.args)))
        if old_yaml_filename is not None:
            if old_yaml_filename != yaml_filename:
                session['i'] = yaml_filename
                if request.args.get('from_list', None) is None and not yaml_filename.startswith("docassemble.playground") and not yaml_filename.startswith("docassemble.base"):
                    show_flash = True
        if session_parameter is None:
            if show_flash:
                if current_user.is_authenticated:
                    message = "Starting a new interview.  To go back to your previous interview, go to My Interviews on the menu."
                else:
                    message = "Starting a new interview.  To go back to your previous interview, log in to see a list of your interviews."
            #logmessage("session parameter is none")
            user_code, user_dict = reset_session(yaml_filename, secret)
            release_lock(user_code, yaml_filename)
            session_id = session.get('uid', None)
            if 'key_logged' in session:
                del session['key_logged']
            need_to_reset = True
        else:
            logmessage("Both i and session provided")
            if show_flash:
                if current_user.is_authenticated:
                    message = "Entering a different interview.  To go back to your previous interview, go to My Interviews on the menu."
                else:
                    message = "Entering a different interview.  To go back to your previous interview, log in to see a list of your interviews."
        if show_flash:
            flash(word(message), 'info')
    if session_parameter is not None:
        logmessage("session parameter is " + str(session_parameter))
        session_id = session_parameter
        session['uid'] = session_id
        if yaml_parameter is not None:
            session['i'] = yaml_filename
        if 'key_logged' in session:
            del session['key_logged']
        need_to_reset = True
    if session_id:
        user_code = session_id
        #logmessage("session id is " + str(session_id))
        obtain_lock(user_code, yaml_filename)
        try:
            steps, user_dict, is_encrypted = fetch_user_dict(user_code, yaml_filename, secret=secret)
        except:
            release_lock(user_code, yaml_filename)
            user_code, user_dict = reset_session(yaml_filename, secret)
            encrypted = False
            session['encrypted'] = encrypted
            is_encrypted = encrypted
            if 'key_logged' in session:
                del session['key_logged']
            need_to_reset = True
        if encrypted != is_encrypted:
            encrypted = is_encrypted
            session['encrypted'] = encrypted
        # if currentsecret is not None:
        #     try:
        #         steps, user_dict = fetch_user_dict(user_code, yaml_filename, secret=currentsecret)
        #         secret_to_use = currentsecret
        #     except:
        #         del session['currentsecret']
        #         currentsecret = None
        #         try:
        #             steps, user_dict = fetch_user_dict(user_code, yaml_filename, secret=secret)
        #             secret_to_use = secret
        #         except:
        #             logmessage("Error: could not get user dict")
        # else:
        #     steps, user_dict = fetch_user_dict(user_code, yaml_filename, secret=secret)
        #     secret_to_use = secret
        if user_dict is None:
            logmessage("user_dict was none")
            try:
                release_lock(user_code, yaml_filename)
            except:
                pass
            del user_code
            del user_dict
    try:
        user_dict
        user_code
    except:
        logmessage("resetting session")
        user_code, user_dict = reset_session(yaml_filename, secret)
        encrypted = False
        session['encrypted'] = encrypted
        if 'key_logged' in session:
            del session['key_logged']
        steps = 0
    action = None
    if user_dict.get('multi_user', False) is True and encrypted is True:
        encrypted = False
        session['encrypted'] = encrypted
        decrypt_session(secret)
        # Added this for locking
        # steps, user_dict, new_is_encrypted = fetch_user_dict(user_code, yaml_filename, secret=secret)
        # user_dict['_internal']['secret'] = ''.join(random.choice(string.ascii_letters) for i in range(16))
        # currentsecret, temptwo = substitute_secret(secret, user_dict['_internal']['secret'])
        # session['currentsecret'] = currentsecret
        # secret_in_use = currentsecret
    if user_dict.get('multi_user', False) is False and encrypted is False:
        encrypt_session(secret)
        encrypted = True
        session['encrypted'] = encrypted
        # Added this for locking
        # steps, user_dict, new_is_encrypted = fetch_user_dict(user_code, yaml_filename, secret=secret)
    if current_user.is_authenticated and 'key_logged' not in session:
        #logmessage("save_user_dict_key called with " + user_code + " and " + yaml_filename)
        save_user_dict_key(user_code, yaml_filename)
        session['key_logged'] = True
    if 'action' in session:
        action = json.loads(myb64unquote(session['action']))
        del session['action']
    if len(request.args):
        if 'action' in request.args:
            session['action'] = request.args['action']
            response = do_redirect(url_for('index'), is_ajax)
            if set_cookie:
                response.set_cookie('secret', secret)
            if expire_visitor_secret:
                response.set_cookie('visitor_secret', '', expires=0)
            release_lock(user_code, yaml_filename)
            return response
        for argname in request.args:
            if argname in ['filename', 'question', 'format', 'index', 'i', 'action', 'from_list', 'session']:
                continue
            if re.match('[A-Za-z_]+', argname):
                exec("url_args['" + argname + "'] = " + repr(request.args.get(argname).encode('unicode_escape')), user_dict)
            need_to_reset = True
    if need_to_reset:
        save_user_dict(user_code, user_dict, yaml_filename, secret=secret, encrypt=encrypted)
        # if current_user.is_authenticated:
        #     save_user_dict_key(user_code, yaml_filename)
        #     session['key_logged'] = True
        response = do_redirect(url_for('index'), is_ajax)
        if set_cookie:
            response.set_cookie('secret', secret)
        if expire_visitor_secret:
            response.set_cookie('visitor_secret', '', expires=0)
        release_lock(user_code, yaml_filename)
        return response
    #logmessage("action is " + str(action))
    post_data = request.form.copy()
    if '_email_attachments' in post_data and '_attachment_email_address' in post_data and '_question_number' in post_data:
        success = False
        question_number = post_data['_question_number']
        attachment_email_address = post_data['_attachment_email_address']
        if '_attachment_include_editable' in post_data:
            if post_data['_attachment_include_editable'] == 'True':
                include_editable = True
            else:
                include_editable = False
            del post_data['_attachment_include_editable']
        else:
            include_editable = False
        del post_data['_question_number']
        del post_data['_email_attachments']
        del post_data['_attachment_email_address']
        logmessage("Got e-mail request for " + str(question_number) + " with e-mail " + str(attachment_email_address) + " and rtf inclusion of " + str(include_editable) + " and using yaml file " + yaml_filename)
        the_user_dict = get_attachment_info(user_code, question_number, yaml_filename, secret)
        if the_user_dict is not None:
            #logmessage("the_user_dict is not none!")
            interview = docassemble.base.interview_cache.get_interview(yaml_filename)
            interview_status = docassemble.base.parse.InterviewStatus(current_info=current_info(yaml=yaml_filename, req=request, action=action))
            interview.assemble(the_user_dict, interview_status)
            if len(interview_status.attachments) > 0:
                #logmessage("there are attachments!")
                attached_file_count = 0
                attachment_info = list()
                for the_attachment in interview_status.attachments:
                    file_formats = list()
                    if 'pdf' in the_attachment['valid_formats'] or '*' in the_attachment['valid_formats']:
                        file_formats.append('pdf')
                    if include_editable or 'pdf' not in file_formats:
                        if 'rtf' in the_attachment['valid_formats'] or '*' in the_attachment['valid_formats']:
                            file_formats.append('rtf')
                        if 'docx' in the_attachment['valid_formats']:
                            file_formats.append('docx')
                    for the_format in file_formats:
                        the_filename = the_attachment['file'][the_format]
                        if the_format == "pdf":
                            mime_type = 'application/pdf'
                        elif the_format == "rtf":
                            mime_type = 'application/rtf'
                        elif the_format == "docx":
                            mime_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                        attachment_info.append({'filename': str(the_attachment['filename']) + '.' + str(the_format), 'path': str(the_filename), 'mimetype': str(mime_type), 'attachment': the_attachment})
                        logmessage("Need to attach to the e-mail a file called " + str(the_attachment['filename']) + '.' + str(the_format) + ", which is located on the server at " + str(the_filename) + ", with mime type " + str(mime_type))
                        attached_file_count += 1
                if attached_file_count > 0:
                    doc_names = list()
                    for attach_info in attachment_info:
                        if attach_info['attachment']['name'] not in doc_names:
                            doc_names.append(attach_info['attachment']['name'])
                    subject = comma_and_list(doc_names)
                    if len(doc_names) > 1:
                        body = "Your " + subject + " are attached."
                    else:
                        body = "Your " + subject + " is attached."
                    html = "<p>" + body + "</p>"
                    logmessage("Need to send an e-mail with subject " + subject + " to " + str(attachment_email_address) + " with " + str(attached_file_count) + " attachment(s)")
                    msg = Message(subject, recipients=[attachment_email_address], body=body, html=html)
                    for attach_info in attachment_info:
                        with open(attach_info['path'], 'rb') as fp:
                            msg.attach(attach_info['filename'], attach_info['mimetype'], fp.read())
                    try:
                        # mail.send(msg)
                        logmessage("Starting to send")
                        async_mail(msg)
                        logmessage("Finished sending")
                        success = True
                    except Exception as errmess:
                        logmessage(str(errmess))
                        success = False
        if success:
            flash(word("Your documents were e-mailed to") + " " + str(attachment_email_address) + ".", 'info')
        else:
            flash(word("Unable to e-mail your documents to") + " " + str(attachment_email_address) + ".", 'error')
    if '_back_one' in post_data and steps > 1:
        steps, user_dict, is_encrypted = fetch_previous_user_dict(user_code, yaml_filename, secret)
        if encrypted != is_encrypted:
            encrypted = is_encrypted
            session['encrypted'] = encrypted
        #logmessage("Went back")
    elif 'filename' in request.args:
        #logmessage("Got a GET statement with filename!")
        the_user_dict = get_attachment_info(user_code, request.args.get('question'), request.args.get('filename'), secret)
        if the_user_dict is not None:
            #logmessage("the_user_dict is not none!")
            interview = docassemble.base.interview_cache.get_interview(request.args.get('filename'))
            interview_status = docassemble.base.parse.InterviewStatus(current_info=current_info(yaml=yaml_filename, req=request, action=action))
            interview.assemble(the_user_dict, interview_status)
            if len(interview_status.attachments) > 0:
                #logmessage("there are attachments!")
                the_attachment = interview_status.attachments[int(request.args.get('index'))]
                the_filename = the_attachment['file'][request.args.get('format')]
                the_format = request.args.get('format')
                #block_size = 4096
                #status = '200 OK'
                if the_format == "pdf":
                    mime_type = 'application/pdf'
                elif the_format == "tex":
                    mime_type = 'application/x-latex'
                elif the_format == "rtf":
                    mime_type = 'application/rtf'
                elif the_format == "docx":
                    mime_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                response = send_file(the_filename, mimetype=str(mime_type), as_attachment=True, attachment_filename=str(the_attachment['filename']) + '.' + str(the_format))
                response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
                release_lock(user_code, yaml_filename)
                return(response)
    if '_checkboxes' in post_data:
        checkbox_fields = json.loads(myb64unquote(post_data['_checkboxes'])) #post_data['_checkboxes'].split(",")
        for checkbox_field in checkbox_fields:
            if checkbox_field not in post_data:
                post_data.add(checkbox_field, 'False')
    something_changed = False
    if '_tracker' in post_data and user_dict['_internal']['tracker'] != int(post_data['_tracker']):
        logmessage("Something changed.")
        #logmessage("user dict has " + str(user_dict['_internal']['tracker']) + " and post data has " + post_data['_tracker'])
        something_changed = True
    if '_track_location' in post_data and post_data['_track_location']:
        logmessage("Found track location of " + post_data['_track_location'])
        the_location = json.loads(post_data['_track_location'])
    else:
        the_location = None
    should_assemble = False
    if something_changed:
        for key in post_data:
            try:
                if key_requires_preassembly.search(from_safeid(key)):
                    should_assemble = True
                    break
            except:
                logmessage("Bad key: " + str(key))
    interview = docassemble.base.interview_cache.get_interview(yaml_filename)
    #logmessage("Getting interview status where action is " + str(action))
    interview_status = docassemble.base.parse.InterviewStatus(current_info=current_info(yaml=yaml_filename, req=request, action=action, location=the_location), tracker=user_dict['_internal']['tracker'])
    if should_assemble:
        #logmessage("Reassembling.")
        interview.assemble(user_dict, interview_status)
    #else:
        #logmessage("I am not assembling.")        
    changed = False
    error_messages = list()
    if '_the_image' in post_data:
        #interview.assemble(user_dict, interview_status)
        file_field = from_safeid(post_data['_save_as']);
        if match_invalid.search(file_field):
            error_messages.append(("error", "Error: Invalid character in file_field: " + file_field))
        else:
            if something_changed and key_requires_preassembly.search(file_field) and not should_assemble:
                interview.assemble(user_dict, interview_status)
            initial_string = 'import docassemble.base.core'
            try:
                exec(initial_string, user_dict)
            except Exception as errMess:
                error_messages.append(("error", "Error: " + str(errMess)))
            if '_success' in post_data and post_data['_success']:
                theImage = base64.b64decode(re.search(r'base64,(.*)', post_data['_the_image']).group(1) + '==')
                #sys.stderr.write("Got theImage and it is " + str(len(theImage)) + " bytes long\n")
                filename = secure_filename('canvas.png')
                file_number = get_new_file_number(session.get('uid', None), filename, yaml_file_name=yaml_filename)
                extension, mimetype = get_ext_and_mimetype(filename)
                new_file = SavedFile(file_number, extension=extension, fix=True)
                new_file.write_content(theImage)
                new_file.finalize()
                #sys.stderr.write("Saved theImage\n")
                the_string = file_field + " = docassemble.base.core.DAFile(" + repr(file_field) + ", filename='" + str(filename) + "', number=" + str(file_number) + ", mimetype='" + str(mimetype) + "', extension='" + str(extension) + "')"
            else:
                the_string = file_field + " = docassemble.base.core.DAFile(" + repr(file_field) + ")"
            #sys.stderr.write(the_string + "\n")
            try:
                exec(the_string, user_dict)
                changed = True
                steps += 1
            except Exception as errMess:
                #sys.stderr.write("Error: " + str(errMess) + "\n")
                error_messages.append(("error", "Error: " + str(errMess)))
    if '_files' in post_data:
        #logmessage("There are files")
        #interview.assemble(user_dict, interview_status)
        file_fields = json.loads(myb64unquote(post_data['_files'])) #post_data['_files'].split(",")
        has_invalid_fields = False
        should_assemble_now = False
        for orig_file_field in file_fields:
            try:
                file_field = from_safeid(orig_file_field)
            except:
                error_messages.append(("error", "Error: Invalid file_field: " + orig_file_field))
                break
            if match_invalid.search(file_field):
                has_invalid_fields = True
                error_messages.append(("error", "Error: Invalid character in file_field: " + file_field))
                break
            if key_requires_preassembly.search(file_field):
                should_assemble_now = True
        if not has_invalid_fields:
            initial_string = 'import docassemble.base.core'
            try:
                exec(initial_string, user_dict)
            except Exception as errMess:
                error_messages.append(("error", "Error: " + str(errMess)))
            if something_changed and should_assemble_now and not should_assemble:
                interview.assemble(user_dict, interview_status)
            for orig_file_field in file_fields:
                #logmessage("There is a file_field")
                if orig_file_field in request.files:
                    #logmessage("There is a file_field in request.files")
                    the_files = request.files.getlist(orig_file_field)
                    if the_files:
                        files_to_process = list()
                        for the_file in the_files:
                            #logmessage("There is a file_field in request.files and it has a type of " + str(type(the_file)) + " and its str representation is " + str(the_file))
                            filename = secure_filename(the_file.filename)
                            file_number = get_new_file_number(session.get('uid', None), filename, yaml_file_name=yaml_filename)
                            extension, mimetype = get_ext_and_mimetype(filename)
                            saved_file = SavedFile(file_number, extension=extension, fix=True)
                            if extension == "jpg" and daconfig.get('imagemagick', 'convert') is not None:
                                unrotated = tempfile.NamedTemporaryFile(suffix=".jpg")
                                rotated = tempfile.NamedTemporaryFile(suffix=".jpg")
                                the_file.save(unrotated.name)
                                call_array = [daconfig.get('imagemagick', 'convert'), str(unrotated.name), '-auto-orient', '-density', '300', 'jpeg:' + rotated.name]
                                result = call(call_array)
                                if result == 0:
                                    saved_file.copy_from(rotated.name)
                                else:
                                    saved_file.copy_from(unrotated.name)
                            else:
                                the_file.save(saved_file.path)
                                saved_file.save()
                            if mimetype == 'video/quicktime' and daconfig.get('avconv', 'avconv') is not None:
                                call_array = [daconfig.get('avconv', 'avconv'), '-i', saved_file.path + '.' + extension, '-vcodec', 'libtheora', '-acodec', 'libvorbis', saved_file.path + '.ogv']
                                result = call(call_array)
                                call_array = [daconfig.get('avconv', 'avconv'), '-i', saved_file.path + '.' + extension, '-vcodec', 'copy', '-acodec', 'copy', saved_file.path + '.mp4']
                                result = call(call_array)
                            if mimetype == 'video/mp4' and daconfig.get('avconv', 'avconv') is not None:
                                call_array = [daconfig.get('avconv', 'avconv'), '-i', saved_file.path + '.' + extension, '-vcodec', 'libtheora', '-acodec', 'libvorbis', saved_file.path + '.ogv']
                                result = call(call_array)
                            if mimetype == 'video/ogg' and daconfig.get('avconv', 'avconv') is not None:
                                call_array = [daconfig.get('avconv', 'avconv'), '-i', saved_file.path + '.' + extension, '-c:v', 'libx264', '-preset', 'veryslow', '-crf', '22', '-c:a', 'libmp3lame', '-qscale:a', '2', '-ac', '2', '-ar', '44100', saved_file.path + '.mp4']
                                result = call(call_array)
                            if mimetype == 'audio/mpeg' and daconfig.get('pacpl', 'pacpl') is not None:
                                call_array = [daconfig.get('pacpl', 'pacpl'), '-t', 'ogg', saved_file.path + '.' + extension]
                                result = call(call_array)
                            if mimetype == 'audio/ogg' and daconfig.get('pacpl', 'pacpl') is not None:
                                call_array = [daconfig.get('pacpl', 'pacpl'), '-t', 'mp3', saved_file.path + '.' + extension]
                                result = call(call_array)
                            if mimetype in ['audio/3gpp'] and daconfig.get('avconv', 'avconv') is not None:
                                call_array = [daconfig.get('avconv', 'avconv'), '-i', saved_file.path + '.' + extension, saved_file.path + '.ogg']
                                result = call(call_array)
                                call_array = [daconfig.get('avconv', 'avconv'), '-i', saved_file.path + '.' + extension, saved_file.path + '.mp3']
                                result = call(call_array)
                            if mimetype in ['audio/x-wav', 'audio/wav'] and daconfig.get('pacpl', 'pacpl') is not None:
                                call_array = [daconfig.get('pacpl', 'pacpl'), '-t', 'mp3', saved_file.path + '.' + extension]
                                result = call(call_array)
                                call_array = [daconfig.get('pacpl', 'pacpl'), '-t', 'ogg', saved_file.path + '.' + extension]
                                result = call(call_array)
                            if extension == "pdf":
                                make_image_files(saved_file.path)
                            saved_file.finalize()
                            files_to_process.append((filename, file_number, mimetype, extension))
                        try:
                            file_field = from_safeid(orig_file_field)
                        except:
                            error_messages.append(("error", "Error: Invalid file_field: " + orig_file_field))
                            break
                        if match_invalid.search(file_field):
                            error_messages.append(("error", "Error: Invalid character in file_field: " + file_field))
                            break
                        if len(files_to_process) > 0:
                            elements = list()
                            indexno = 0
                            for (filename, file_number, mimetype, extension) in files_to_process:
                                elements.append("docassemble.base.core.DAFile('" + file_field + "[" + str(indexno) + "]', filename='" + str(filename) + "', number=" + str(file_number) + ", mimetype='" + str(mimetype) + "', extension='" + str(extension) + "')")
                                indexno += 1
                            the_string = file_field + " = docassemble.base.core.DAFileList('" + file_field + "', elements=[" + ", ".join(elements) + "])"
                        else:
                            the_string = file_field + " = None"
                        logmessage("Doing " + the_string)
                        try:
                            exec(the_string, user_dict)
                            changed = True
                            steps += 1
                        except Exception as errMess:
                            sys.stderr.write("Error: " + str(errMess) + "\n")
                            error_messages.append(("error", "Error: " + str(errMess)))
                        #post_data.add(file_field, str(file_number))
    known_datatypes = dict()
    if '_datatypes' in post_data:
        #logmessage(myb64unquote(post_data['_datatypes']))
        known_datatypes = json.loads(myb64unquote(post_data['_datatypes']))
    known_varnames = dict()
    if '_varnames' in post_data:
        known_varnames = json.loads(myb64unquote(post_data['_varnames']))
    known_variables = dict()
    for orig_key in copy.deepcopy(post_data):
        if orig_key in ['_checkboxes', '_back_one', '_files', '_question_name', '_the_image', '_save_as', '_success', '_datatypes', '_tracker', '_track_location', '_varnames', 'ajax', 'informed']:
            continue
        try:
            key = myb64unquote(orig_key)
        except:
            continue
        if key.startswith('_field_') and orig_key in known_varnames:
            post_data[known_varnames[orig_key]] = post_data[orig_key]
    for orig_key in post_data:
        if orig_key in ['_checkboxes', '_back_one', '_files', '_question_name', '_the_image', '_save_as', '_success', '_datatypes', '_tracker', '_track_location', '_varnames', 'ajax', 'informed']:
            continue
        #logmessage("Got a key: " + key)
        data = post_data[orig_key]
        try:
            key = myb64unquote(orig_key)
        except:
            raise DAError("invalid name " + str(orig_key))
        #data = re.sub(r'"""', '', data)
        if key.startswith('_field_'):
            continue
        bracket_expression = None
        if match_brackets.search(key):
            #logmessage("Searching key " + str(key))
            match = match_inside_and_outside_brackets.search(key)
            try:
                key = match.group(1)
            except:
                raise DAError("invalid name " + str(match.group(1)))
            real_key = safeid(key)
            if match_invalid.search(key):
                error_messages.append(("error", "Error: Invalid character in key: " + key))
                break
            b_match = match_inside_brackets.search(match.group(2))
            if b_match:
                try:
                    bracket_expression = from_safeid(b_match.group(1))
                except:
                    bracket_expression = b_match.group(1)
            bracket = match_inside_brackets.sub(process_bracket_expression, match.group(2))
            #logmessage("key is " + str(key) + " and bracket is " + str(bracket))
            if key in user_dict:
                known_variables[key] = True
            if key not in known_variables:
                try:
                    eval(key, user_dict)
                except:
                    #logmessage("setting key " + str(key) + " to empty dict")
                    the_string = key + ' = dict()'
                    try:
                        exec(the_string, user_dict)
                        known_variables[key] = True
                    except:
                        raise DAError("cannot initialize " + key)
            key = key + bracket
        else:
            real_key = orig_key
            if match_invalid_key.search(key):
                error_messages.append(("error", "Error: Invalid character in key: " + key))
                break
        #logmessage("Real key is " + real_key + " and key is " + key)
        do_append = False
        do_opposite = False
        if real_key in known_datatypes:
            #logmessage("key " + real_key + "is in datatypes: " + known_datatypes[key])
            if known_datatypes[real_key] in ['boolean', 'checkboxes', 'yesno', 'noyes', 'yesnowide', 'noyeswide']:
                if data == "True":
                    data = "True"
                else:
                    data = "False"
            elif known_datatypes[real_key] in ['threestate', 'yesnomaybe', 'noyesmaybe', 'yesnowidemaybe', 'noyeswidemaybe']:
                if data == "True":
                    data = "True"
                elif data == "None":
                    data = "None"
                else:
                    data = "False"
            elif known_datatypes[real_key] == 'integer':
                if data == '':
                    data = 0
                data = "int(" + repr(data) + ")"
            elif known_datatypes[real_key] in ['number', 'float', 'currency', 'range']:
                if data == '':
                    data = 0
                data = "float(" + repr(data) + ")"
            elif known_datatypes[real_key] in ['object', 'object_radio']:
                if data == '':
                    continue
                #logmessage("Got to here")
                data = "_internal['objselections'][" + repr(key) + "][" + repr(data) + "]"
            elif known_datatypes[real_key] in ['object_checkboxes'] and bracket_expression is not None:
                if data not in ['True', 'False', 'None']:
                    continue
                do_append = True
                if data == 'False':
                    do_opposite = True
                data = "_internal['objselections'][" + repr(from_safeid(real_key)) + "][" + repr(bracket_expression) + "]"
            else:
                if type(data) in [str, unicode]:
                    data = data.strip()
                data = repr(data)
            if known_datatypes[real_key] in ['object_checkboxes']:
                do_append = True
        elif key == "_multiple_choice":
            #logmessage("key is multiple choice")
            data = "int(" + repr(data) + ")"
        else:
            logmessage("key is not in datatypes where datatypes is " + str(known_datatypes))
            data = repr(data)
        if key == "_multiple_choice":
            #interview.assemble(user_dict, interview_status)
            #if interview_status.question.question_type == "multiple_choice" and not hasattr(interview_status.question.fields[0], 'saveas'):
                #key = '_internal["answers"]["' + interview_status.question.name + '"]'
            if '_question_name' in post_data:
                key = '_internal["answers"][' + repr(post_data['_question_name']) + ']'
            #else:
                #continue
                #error_messages.append(("error", "Error: multiple choice values were supplied, but docassemble was not waiting for an answer to a multiple choice question."))
        if do_append:
            key_to_use = from_safeid(real_key)
            if do_opposite:
                the_string = 'if ' + data + ' in ' + key_to_use + ':\n    ' + key_to_use + '.remove(' + data + ')'
            else:
                the_string = 'if ' + data + ' not in ' + key_to_use + ':\n    ' + key_to_use + '.append(' + data + ')'
        else:
            the_string = key + ' = ' + data
        logmessage("Doing " + str(the_string))
        try:
            exec(the_string, user_dict)
            changed = True
            steps += 1
        except Exception as errMess:
            error_messages.append(("error", "Error: " + str(errMess)))
    if 'informed' in request.form:
        if current_user.is_anonymous:
            the_user_id = 't' + str(session['tempuser'])
        else:
            the_user_id = str(current_user.id)
        user_dict['_internal']['informed'][the_user_id] = dict()
        for key in request.form['informed'].split(','):
            user_dict['_internal']['informed'][the_user_id][key] = 1
    # if 'x' in user_dict:
    #     del user_dict['x']
    # if 'i' in user_dict:
    #     del user_dict['i']
    # if changed and '_question_name' in post_data:
        # user_dict['_internal']['answered'].add(post_data['_question_name'])
        # logmessage("From server.py, answered name is " + post_data['_question_name'])
        # user_dict['role_event_notification_sent'] = False
    if changed and '_question_name' in post_data and post_data['_question_name'] not in user_dict['_internal']['answers']:
        user_dict['_internal']['answered'].add(post_data['_question_name'])
    # if '_multiple_choice' in post_data and '_question_name' in post_data and post_data['_question_name'] in interview.questions_by_name and not interview.questions_by_name[post_data['_question_name']].is_generic:
    #     interview_status.populate(interview.questions_by_name[post_data['_question_name']].ask(user_dict, 'None', 'None'))
    # else:
    interview.assemble(user_dict, interview_status)
    if not interview_status.can_go_back:
        user_dict['_internal']['steps_offset'] = steps
    if len(interview_status.attachments) > 0:
        #logmessage("Updating attachment info")
        update_attachment_info(user_code, user_dict, interview_status, secret)
    if interview_status.question.question_type == "restart":
        manual_checkout()
        url_args = user_dict['url_args']
        user_dict = fresh_dictionary()
        user_dict['url_args'] = url_args
        interview_status = docassemble.base.parse.InterviewStatus(current_info=current_info(yaml=yaml_filename, req=request))
        reset_user_dict(user_code, yaml_filename)
        save_user_dict(user_code, user_dict, yaml_filename, secret=secret)
        if current_user.is_authenticated and 'visitor_secret' not in request.cookies:
            save_user_dict_key(user_code, yaml_filename)
            session['key_logged'] = True
        steps = 0
        changed = False
        interview.assemble(user_dict, interview_status)
    if interview_status.question.question_type == "refresh":
        release_lock(user_code, yaml_filename)
        return do_redirect(url_for('index'), is_ajax)
    if interview_status.question.question_type == "signin":
        release_lock(user_code, yaml_filename)
        return do_redirect(url_for('user.login'), is_ajax)
    if interview_status.question.question_type == "leave":
        release_lock(user_code, yaml_filename)
        if interview_status.questionText != '':
            return do_redirect(interview_status.questionText, is_ajax)
        else:
            return do_redirect(exit_page, is_ajax)
    if interview_status.question.interview.use_progress_bar and interview_status.question.progress is not None and interview_status.question.progress > user_dict['_internal']['progress']:
        user_dict['_internal']['progress'] = interview_status.question.progress
    if interview_status.question.question_type == "exit":
        manual_checkout()
        user_dict = fresh_dictionary()
        reset_user_dict(user_code, yaml_filename)
        save_user_dict(user_code, user_dict, yaml_filename, secret=secret)
        if current_user.is_authenticated and 'visitor_secret' not in request.cookies:
            save_user_dict_key(user_code, yaml_filename)
            session['key_logged'] = True
        release_lock(user_code, yaml_filename)
        if interview_status.questionText != '':
            return do_redirect(interview_status.questionText, is_ajax)
        else:
            return do_redirect(exit_page, is_ajax)
    if interview_status.question.question_type == "response":
        # Duplicative to save here?
        #save_user_dict(user_code, user_dict, yaml_filename, secret=secret, changed=changed, encrypt=encrypted)
        if is_ajax:
            release_lock(user_code, yaml_filename)
            return jsonify(action='resubmit')
        else:
            if hasattr(interview_status.question, 'binaryresponse'):
                response_to_send = make_response(interview_status.question.binaryresponse, '200 OK')
            else:
                response_to_send = make_response(interview_status.questionText.encode('utf8'), '200 OK')
            response_to_send.headers['Content-type'] = interview_status.extras['content_type']
        if set_cookie:
            response_to_send.set_cookie('secret', secret)
        if expire_visitor_secret:
            response.set_cookie('visitor_secret', '', expires=0)
    elif interview_status.question.question_type == "sendfile":
        if is_ajax:
            release_lock(user_code, yaml_filename)
            return jsonify(action='resubmit')
        else:
            # Duplicative to save here?  Just for the 404?
            #save_user_dict(user_code, user_dict, yaml_filename, secret=secret, changed=changed, encrypt=encrypted)
            the_path = interview_status.question.response_filename
            if not os.path.isfile(the_path):
                logmessage("Could not send file because file (" + the_path + ") not found")
                abort(404)
            response_to_send = send_file(the_path, mimetype=interview_status.extras['content_type'])
            response_to_send.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        if set_cookie:
            response_to_send.set_cookie('secret', secret)
        if expire_visitor_secret:
            response.set_cookie('visitor_secret', '', expires=0)
    elif interview_status.question.question_type == "redirect":
        # Duplicative to save here?
        #save_user_dict(user_code, user_dict, yaml_filename, secret=secret, changed=changed, encrypt=encrypted)
        response_to_send = do_redirect(interview_status.questionText, is_ajax)
    else:
        response_to_send = None
    # Why do this?  To prevent loops of redirects?
    user_dict['_internal']['answers'] = dict()
    if interview_status.question.name and interview_status.question.name in user_dict['_internal']['answers']:
        del user_dict['_internal']['answers'][interview_status.question.name]
    if changed and interview_status.question.interview.use_progress_bar:
        advance_progress(user_dict)
    save_user_dict(user_code, user_dict, yaml_filename, secret=secret, changed=changed, encrypt=encrypted)
    if user_dict.get('multi_user', False) is True and encrypted is True:
        encrypted = False
        session['encrypted'] = encrypted
        decrypt_session(secret)
    if user_dict.get('multi_user', False) is False and encrypted is False:
        encrypt_session(secret)
        encrypted = True
        session['encrypted'] = encrypted
    if response_to_send is not None:
        release_lock(user_code, yaml_filename)
        return response_to_send
    flash_content = ""
    messages = get_flashed_messages(with_categories=True) + error_messages
    if messages and len(messages):
        flash_content += '<div class="topcenter col-centered col-sm-7 col-md-6 col-lg-5" id="flash">'
        for classname, message in messages:
            if classname == 'error':
                classname = 'danger'
            flash_content += '<div class="alert alert-' + classname + '"><button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>' + message + '</div>'
        flash_content += '</div>'
#     scripts = """
#     <script src="//ajax.googleapis.com/ajax/libs/jquery/2.2.0/jquery.min.js"></script>
#     <script src="//ajax.aspnetcdn.com/ajax/jquery.validate/1.14.0/jquery.validate.min.js"></script>
#     <script src="//maxcdn.bootstrapcdn.com/bootstrap/3.3.6/js/bootstrap.min.js"></script>
#     <script src="//cdnjs.cloudflare.com/ajax/libs/jasny-bootstrap/3.1.3/js/jasny-bootstrap.min.js"></script>
# """
        # $(function () {
        #   $('.tabs a:last').tab('show')
        # })
    if not is_ajax:
        scripts = standard_scripts()
        chat_available = user_dict['_internal']['chat']['availability']
        chat_mode = user_dict['_internal']['chat']['mode']
        if chat_available == 'unavailable':
            chat_status = 'off'
            session['chatstatus'] = 'off'
        else:
            chat_status = chatstatus
        if chat_status in ['ready', 'on']:
            chat_status = 'ringing'
            session['chatstatus'] = 'ringing'
        if chat_status != 'off':
            send_changes = 'true'
        else:
            send_changes = 'false'
        if current_user.is_authenticated:
            user_id_string = str(current_user.id)
            if current_user.has_role('admin', 'developer', 'advocate'):
                is_user = 'false'
            else:
                is_user = 'true'
        else:
            user_id_string = 't' + str(session['tempuser'])
            is_user = 'true'
#      var daUserId = """ + repr(str(user_id_string)) + """;
        scripts += """    <script type="text/javascript" charset="utf-8">
      var socket = null;
      var foobar = null;
      var chatHistory = [];
      var daCheckingIn = 0;
      var daShowingHelp = 0;
      var daIsUser = """ + is_user + """;
      var daChatStatus = """ + repr(str(chat_status)) + """;
      var daChatAvailable = """ + repr(str(chat_available)) + """;
      var daPhoneAvailable = false;
      var daChatMode = """ + repr(str(chat_mode)) + """;
      var daSendChanges = """ + send_changes + """;
      var daInitialized = false;
      var notYetScrolled = true;
      var daInformedChanged = false;
      var daInformed = """ + json.dumps(user_dict['_internal']['informed'].get(user_id_string, dict())) + """;
      function userNameString(data){
          if (data.hasOwnProperty('temp_user_id')){
              return """ + repr(str(word("anonymous visitor"))) + """ + ' ' + data.temp_user_id;
          }
          else{
              if (data.first_name && data.first_name != ''){
                  return data.first_name + ' ' + data.last_name;
              }
              else{
                  return data.email;
              }
          }
      }
      function inform_about(subject){
        if (subject in daInformed || !daIsUser){
          return;
        }
        if (daShowingHelp){
          daInformed[subject] = 1;
          daInformedChanged = true;
          return;
        }
        var target;
        var message;
        var waitPeriod = 3000;
        if (subject == 'chat'){
          target = "#daChatAvailable i";
          message = """ + repr(str(word("Get help through live chat by clicking here."))) + """;
        }
        else if (subject == 'chatmessage'){
          target = "#daChatAvailable i";
          message = """ + repr(str(word("A chat message has arrived."))) + """;
        }
        else if (subject == 'phone'){
          target = "#daPhoneAvailable i";
          message = """ + repr(str(word("Click here to get help over the phone."))) + """;
        }
        else{
          return;
        }
        if (subject != 'chatmessage'){
          daInformed[subject] = 1;
          daInformedChanged = true;
        }
        $(target).popover({"content": message, "placement": "bottom", "trigger": "manual", "container": "body"});
        $(target).popover('show');
        setTimeout(function(){
          $(target).popover('destroy');
          $(target).removeAttr('title');
        }, waitPeriod);
      }
      function daCloseSocket(){
        if (typeof socket !== 'undefined'){
          //socket.emit('terminate');
          //io.unwatch();
        }
      }
      function publishMessage(data){
        var newDiv = document.createElement('li');
        $(newDiv).addClass("list-group-item");
        if (data.is_self){
          $(newDiv).addClass("list-group-item-warning dalistright");
        }
        else{
          $(newDiv).addClass("list-group-item-info");
        }
        //var newSpan = document.createElement('span');
        //$(newSpan).html(data.message);
        //$(newSpan).appendTo($(newDiv));
        //var newName = document.createElement('span');
        //$(newName).html(userNameString(data));
        //$(newName).appendTo($(newDiv));
        $(newDiv).html(data.message);
        $("#daCorrespondence").append(newDiv);
      }
      function scrollChat(){
        var chatScroller = $("#daCorrespondence");
        if (chatScroller.length){
          var height = chatScroller[0].scrollHeight;
          //console.log("Slow scrolling to " + height)
          if (height == 0){
            notYetScrolled = true;
            return;
          }
          chatScroller.animate({scrollTop: height}, 800);
        }
        else{
          console.log("scrollChat: error")
        }
      }
      function scrollChatFast(){
        var chatScroller = $("#daCorrespondence");
        if (chatScroller.length){
          var height = chatScroller[0].scrollHeight;
          if (height == 0){
            notYetScrolled = true;
            return;
          }
          //console.log("Scrolling to " + height + " where there are " + chatScroller[0].childElementCount + " children");
          chatScroller.scrollTop(height);
        }
        else{
          console.log("scrollChatFast: error");
        }
      }
      function daSender(){
        //console.log("Clicked it")
        if ($("#daMessage").val().length){
          socket.emit('chatmessage', {data: $("#daMessage").val()});
          $("#daMessage").val("");
          $("#daMessage").focus();
        }
        return false;
      }
      function daInitializeSocket(){
        if (socket != null){
            if (socket.connected){
                //console.log("Calling connectagain")
                socket.emit('connectagain', {data: 1});
            }
            else{
                socket.connect();
            }
            return;
        }
        if (location.protocol === 'http:' || document.location.protocol === 'http:'){
            socket = io.connect("http://" + document.domain + "/interview", {path: '/ws/socket.io'});
        }
        if (location.protocol === 'https:' || document.location.protocol === 'https:'){
            socket = io.connect("https://" + document.domain + "/interview" + location.port, {path: '/wss/socket.io'});
        }
        if (socket != null){
            socket.on('connect', function() {
                if (socket == null){
                  console.log("Error: socket is null");
                  return;
                }
                //console.log("Connected socket with sid " + socket.id);
                daChatStatus = 'on';
                display_chat();
                pushChanges();
                //daTurnOnChat();
                //console.log("Emitting chat_log from on connect");
                socket.emit('chat_log', {data: 1});
            });
            socket.on('chat_log', function(arg) {
                //console.log("Got chat_log");
                $("#daCorrespondence").html('');
                chatHistory = []; 
                var messages = arg.data;
                for (var i = 0; i < messages.length; ++i){
                    chatHistory.push(messages[i]);
                    publishMessage(messages[i]);
                }
                scrollChatFast();
            });
            socket.on('chatready', function(data) {
                //var key = 'da:session:uid:' + data.uid + ':i:' + data.i + ':userid:' + data.userid
                //console.log('chatready');
            });
            socket.on('terminate', function() {
                //console.log("Terminating socket");
                socket.disconnect();
            });
            socket.on('disconnect', function() {
                //console.log("Disconnected socket");
                //socket = null;
            });
            socket.on('reconnected', function() {
                //console.log("Reconnected")
                daChatStatus = 'on';
                display_chat();
                pushChanges();
                daTurnOnChat();
                //console.log("Emitting chat_log from reconnected");
                socket.emit('chat_log', {data: 1});
            });
            socket.on('mymessage', function(arg) {
                //console.log("Received " + arg.data);
                $("#daPushResult").html(arg.data);
            });
            socket.on('departure', function(arg) {
                //console.log("Departure " + arg.numpartners);
                if (arg.numpartners == 0){
                    daCloseChat();
                }
            });
            socket.on('chatmessage', function(arg) {
                //console.log("Received chat message " + arg.data);
                chatHistory.push(arg.data);
                publishMessage(arg.data);
                scrollChat();
                inform_about('chatmessage');
            });
        }
      }
      var checkinInterval = null;
      var daReloader = null;
      var dadisable = null;
      var daSubmitter = null;
      var daChatRoles = """ + json.dumps(user_dict['_internal']['chat']['roles']) + """;
      var daChatPartnerRoles = """ + json.dumps(user_dict['_internal']['chat']['partner_roles']) + """;
      function pushChanges(){
        if (checkinInterval != null){
          clearInterval(checkinInterval);
        }
        daCheckin();
        checkinInterval = setInterval(daCheckin, 6000);
      }
      function daProcessAjaxError(xhr, status, error){
        //console.log("Got error: " + error);
        //console.log("Status was: " + status);
        $("body").html(xhr.responseText);
      }
      function daProcessAjax(data, form){
        daInformedChanged = false;
        if (dadisable != null){
          clearTimeout(dadisable);
        }
        if (data.action == 'body'){
          $("body").html(data.body);
          $("body").removeClass();
          $("body").addClass(data.bodyclass);
          daChatAvailable = data.chat.available;
          daChatMode = data.chat.mode;
          daChatRoles = data.chat.roles;
          daChatPartnerRoles = data.chat.partner_roles;
          daInitialize();
          var tempDiv = document.createElement('div');
          tempDiv.innerHTML = data.extra_scripts;
          var scripts = tempDiv.getElementsByTagName('script');
          for (var i = 0; i < scripts.length; i++){
            eval(scripts[i].innerHTML);
          }
          for (var i = 0; i < data.extra_css.length; i++){
            $("head").append(data.extra_css[i]);
          }
          document.title = data.browser_title;
          if ($("html").attr("lang") != data.lang){
            $("html").attr("lang", data.lang);
          }
          if (daReloader != null){
            clearTimeout(daReloader);
          }
          if (data.reload_after != null){
            daReloader = setTimeout(function(){location.reload();}, data.reload_after);
          }
        }
        else if (data.action == 'redirect'){
          window.location = data.url;
        }
        else if (data.action == 'resubmit'){
          if (daSubmitter != null){
            var input = $("<input>")
              .attr("type", "hidden")
              .attr("name", daSubmitter.name).val(daSubmitter.value);
            $(form).append($(input));
          }
          form.submit();
        }
      }
      function daRingChat(){
        daChatStatus = 'ringing';
        pushChanges();
      }
      function daTurnOnChat(){
        //console.log("Publishing from daTurnOnChat");
        $("#daChatOnButton").addClass("invisible");
        $("#daChatBox").removeClass("invisible");
        $("#daCorrespondence").html('');
        for(var i = 0; i < chatHistory.length; i++){
          publishMessage(chatHistory[i]);
        }
        scrollChatFast();
        $("#daMessage").prop('disabled', false);
        if (daShowingHelp){
          $("#daMessage").focus();
        }
      }
      function daCloseChat(){
        daChatStatus = 'hangup';
        pushChanges();
        if (socket != null && socket.connected){
          socket.disconnect();
        }
      }
      // function daTurnOffChat(){
      //   $("#daChatOnButton").removeClass("invisible");
      //   $("#daChatBox").addClass("invisible");
      //   //daCloseSocket();
      //   $("#daMessage").prop('disabled', true);
      //   $("#daSend").unbind();
      //   //daStartCheckingIn();
      // }
      function display_chat(){
        if (daChatStatus == 'off'){
          $("#daChatBox").addClass("invisible");
          $("#daChatAvailable").addClass("invisible");
          $("#daChatOnButton").addClass("invisible");
        }
        if (daChatStatus != 'off'){
          $("#daChatBox").removeClass("invisible");
        }
        if (daChatStatus == 'waiting'){
          //console.log("I see waiting")
          if (chatHistory.length > 0){
            $("#daChatAvailable i").removeClass("chat-active");
            $("#daChatAvailable i").addClass("chat-inactive");
            $("#daChatAvailable").removeClass("invisible");
          }
          else{
            $("#daChatAvailable i").removeClass("chat-active");
            $("#daChatAvailable i").removeClass("chat-inactive");
            $("#daChatAvailable").addClass("invisible");
          }
          $("#daChatOnButton").addClass("invisible");
          $("#daChatOffButton").addClass("invisible");
          $("#daMessage").prop('disabled', true);
          $("#daSend").prop('disabled', true);
        }
        if (daChatStatus == 'standby' || daChatStatus == 'ready'){
          //console.log("I see standby")
          $("#daChatAvailable").removeClass("invisible");
          $("#daChatAvailable i").removeClass("chat-inactive");
          $("#daChatAvailable i").addClass("chat-active");
          $("#daChatOnButton").removeClass("invisible");
          $("#daChatOffButton").addClass("invisible");
          $("#daMessage").prop('disabled', true);
          $("#daSend").prop('disabled', true);
          inform_about('chat');
        }
        if (daChatStatus == 'on'){
          $("#daChatAvailable").removeClass("invisible");
          $("#daChatAvailable i").removeClass("chat-inactive");
          $("#daChatAvailable i").addClass("chat-active");
          $("#daChatOnButton").addClass("invisible");
          $("#daChatOffButton").removeClass("invisible");
          $("#daMessage").prop('disabled', false);
          if (daShowingHelp){
            $("#daMessage").focus();
          }
          $("#daSend").prop('disabled', false);
          inform_about('chat');
        }
      }
      function daChatLogCallback(data){
        //console.log("daChatLogCallback: success is " + data.success);
        if (data.success){
          $("#daCorrespondence").html('');
          chatHistory = []; 
          var messages = data.messages;
          for (var i = 0; i < messages.length; ++i){
            chatHistory.push(messages[i]);
            publishMessage(messages[i]);
          }
          display_chat();
          scrollChatFast();
        }
      }
      function daCheckinCallback(data){
        daCheckingIn = 0;
        //console.log("success is " + data.success);
        if (data.success){
          oldDaChatStatus = daChatStatus;
          //console.log("daCheckinCallback: from " + daChatStatus + " to " + data.chat_status);
          if (data.phone == null){
            $("#daPhoneMessage").addClass("invisible");
            $("#daPhoneMessage p").html('');
            $("#daPhoneAvailable").addClass("invisible");
            daPhoneAvailable = false;
          }
          else{
            $("#daPhoneMessage").removeClass("invisible");
            $("#daPhoneMessage p").html(data.phone);
            $("#daPhoneAvailable").removeClass("invisible");
            daPhoneAvailable = true;
            inform_about('phone');
          }
          var statusChanged;
          if (daChatStatus == data.chat_status){
            statusChanged = false;
          }
          else{
            statusChanged = true;
          }
          if (statusChanged){
            daChatStatus = data.chat_status;
            display_chat();
            if (daChatStatus == 'ready'){
              //console.log("calling initialize socket because ready");
              daInitializeSocket();
            }
          }
          if (daChatMode == 'peer' || daChatMode == 'peerhelp'){
            if (data.num_peers == 1){
              $("#peerMessage").html('<span class="badge btn-info">' + data.num_peers + ' """ + word("other user") + """</span>');
            }
            else{
              $("#peerMessage").html('<span class="badge btn-info">' + data.num_peers + ' """ + word("other users") + """</span>');
            }
            $("#peerMessage").removeClass("invisible");
          }
          else{
            $("#peerMessage").addClass("invisible");
          }
          if (daChatMode == 'peerhelp' || daChatMode == 'help'){
            if (data.help_available == 1){
              $("#peerHelpMessage").html('<span class="badge btn-primary">' + data.help_available + ' """ + word("operator") + """</span>');
            }
            else{
              $("#peerHelpMessage").html('<span class="badge btn-primary">' + data.help_available + ' """ + word("operators") + """</span>');
            }
            $("#peerHelpMessage").removeClass("invisible");
          }
          else{
            $("#peerHelpMessage").addClass("invisible");
          }
        }
      }
      function daCheckoutCallback(data){
      }
      function daCheckin(){
        daCheckingIn += 1;
        if (daCheckingIn > 1 && !(daCheckingIn % 3)){
          console.log("daCheckin: request already pending, not re-sending");
          return;
        }
        var datastring;
        if ((daChatStatus == 'waiting' || daChatStatus == 'standby' || daChatStatus == 'ringing' || daChatStatus == 'ready' || daChatStatus == 'on') && $("#daform").length > 0){
          datastring = $.param({action: 'checkin', chatstatus: daChatStatus, chatmode: daChatMode, parameters: JSON.stringify($("#daform").serializeArray())});
        }
        else{
          datastring = $.param({action: 'checkin', chatstatus: daChatStatus, chatmode: daChatMode});
        }
        //console.log("Doing checkin with " + daChatStatus);
        $.ajax({
          type: 'POST',
          url: """ + "'" + url_for('checkin') + "'" + """,
          data: datastring,
          success: daCheckinCallback,
          dataType: 'json'
        });
        return true;
      }
      function daCheckout(){
        $.ajax({
          type: 'POST',
          url: """ + "'" + url_for('checkout') + "'" + """,
          data: 'action=checkout',
          success: daCheckoutCallback,
          dataType: 'json'
        });
        return true;
      }
      function daStopCheckingIn(){
        daCheckout();
        if (checkinInterval != null){
          clearInterval(checkinInterval);
        }
      }
      function daStartCheckingIn(){
        daStopCheckingIn();
        checkinInterval = setInterval(daCheckin, 6000);
      }
      function daInitialize(){
        notYetScrolled = true;
        $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
          if ($(e.target).attr("href") == '#help'){
            daShowingHelp = 1;
            if (notYetScrolled){
              scrollChatFast();
              notYetScrolled = false;
            }
          }
          else{
            daShowingHelp = 0;
          }
        });
        $(function () {
          $('[data-toggle="popover"]').popover({trigger: 'click focus', html: true})
        });
        if (daPhoneAvailable){
          $("#daPhoneAvailable").removeClass("invisible");
        }
        $("#daChatOnButton").click(daRingChat);
        $("#daChatOffButton").click(daCloseChat);
        $('#daMessage').bind('keypress keydown keyup', function(e){
          if(e.keyCode == 13) { daSender(); e.preventDefault(); }
        });
        $('#daform button[type="submit"]').click(function(){
          daSubmitter = this;
        });
        $('#daform input[type="submit"]').click(function(){
          daSubmitter = this;
        });
        $("#daform input, #daform textarea, #daform select").first().each(function(){
          $(this).focus();
          var inputType = $(this).attr('type');
          if ($(this).prop('tagName') != 'SELECT' && inputType != "checkbox" && inputType != "radio" && inputType != "hidden" && inputType != "submit" && inputType != "file" && inputType != "range"){
            var strLength = $(this).val().length * 2;
            $(this)[0].setSelectionRange(strLength, strLength);
          }
        });
        $(".to-labelauty").labelauty({ width: "100%" });
        $(".to-labelauty-icon").labelauty({ label: false });
        $(function(){ 
          var navMain = $("#navbar-collapse");
          navMain.on("click", "a", null, function () {
            if (!($(this).hasClass("dropdown-toggle"))){
              navMain.collapse('hide');
            }
          });
          $("#helptoggle").on("click", function(){
            //console.log("Got to helptoggle");
            window.scrollTo(0, 0);
            $(this).removeClass('daactivetext')
          });
          $("#sourcetoggle").on("click", function(){
            $(this).toggleClass("sourceactive");
          });
          $('#backToQuestion').click(function(event){
            event.preventDefault();
            $('#questionlabel').trigger('click');
          });
        });
        $(".showif").each(function(){
          var showIfSign = $(this).data('showif-sign');
          var showIfVar = $(this).data('showif-var');
          var showIfVarEscaped = showIfVar.replace(/(:|\.|\[|\]|,|=)/, "\\\\$1");
          var showIfVal = $(this).data('showif-val');
          var saveAs = $(this).data('saveas');
          var isSame = (saveAs == showIfVar);
          var showIfDiv = this;
          var showHideDiv = function(){
            //console.log("showHideDiv1")
            if($(this).parents(".showif").length !== 0){
              return;
            }
            var theVal;
            if ($(this).attr('type') == "checkbox" || $(this).attr('type') == "radio"){
              theVal = $("input[name='" + showIfVarEscaped + "']:checked").val();
            }
            else{
              theVal = $(this).val();
            }
            //console.log("val is " + theVal + " and showIfVal is " + showIfVal)
            if(theVal == showIfVal){
              //console.log("They are the same");
              if (showIfSign){
                $(showIfDiv).removeClass("invisible");
                $(showIfDiv).find('input, textarea, select').prop("disabled", false);
              }
              else{
                $(showIfDiv).addClass("invisible");
                $(showIfDiv).find('input, textarea, select').prop("disabled", true);
              }
            }
            else{
              //console.log("They are not the same");
              if (showIfSign){
                $(showIfDiv).addClass("invisible");
                $(showIfDiv).find('input, textarea, select').prop("disabled", true);
              }
              else{
                $(showIfDiv).removeClass("invisible");
                $(showIfDiv).find('input, textarea, select').prop("disabled", false);
              }
            }
          };
          $("#" + showIfVarEscaped).each(showHideDiv);
          $("#" + showIfVarEscaped).change(showHideDiv);
          $("input[type='radio'][name='" + showIfVarEscaped + "']").each(showHideDiv);
          $("input[type='radio'][name='" + showIfVarEscaped + "']").change(showHideDiv);
          $("input[type='checkbox'][name='" + showIfVarEscaped + "']").each(showHideDiv);
          $("input[type='checkbox'][name='" + showIfVarEscaped + "']").change(showHideDiv);
        });
        $("#daSend").click(daSender);
        if (daChatAvailable == 'unavailable'){
          daChatStatus = 'off';
        }
        if (daChatStatus == 'off' && daChatAvailable == 'available'){
          daChatStatus = 'waiting';
        }
        display_chat();
        if (daChatStatus == 'ready'){
          daInitializeSocket();
        }
        if (true || daInitialized == false){
          setTimeout(function(){
            //console.log("daInitialize call to chat_log in checkin");
            $.ajax({
              type: 'POST',
              url: """ + "'" + url_for('checkin') + "'" + """,
              data: $.param({action: 'chat_log'}),
              success: daChatLogCallback,
              dataType: 'json'
            });
          }, 200);
        }
        if (daInitialized == true){
          //console.log("Publishing from memory");
          $("#daCorrespondence").html('');
          for(var i = 0; i < chatHistory.length; i++){
            publishMessage(chatHistory[i]);
          }
        }
        if (daChatStatus != 'off'){
          daSendChanges = true;
        }
        else{
          daSendChanges = false;
        }
        if (daSendChanges){
          $("#daform").each(function(){
            $(this).find(':input').change(pushChanges);
          });
        }
        daInitialized = true;
        daShowingHelp = 0;
      }
      $( document ).ready(function(){
        daInitialize();
        setTimeout(daCheckin, 100);
        checkinInterval = setInterval(daCheckin, 6000);
        $( window ).unload(function() {
          daStopCheckingIn();
          if (socket != null && socket.connected){
            socket.emit('terminate');
          }
        });
      });
    </script>"""
    if interview_status.question.language != '*':
        interview_language = interview_status.question.language
    else:
        interview_language = DEFAULT_LANGUAGE
    extra_scripts = list()
    extra_css = list()
    validation_rules = {'rules': {}, 'messages': {}, 'errorClass': 'help-inline'}
    if interview_status.question.language != '*':
        interview_language = interview_status.question.language
    else:
        interview_language = DEFAULT_LANGUAGE
    if 'reload_after' in interview_status.extras:
        reload_after = '\n    <meta http-equiv="refresh" content="' + str(interview_status.extras['reload_after']) + '">'
    else:
        reload_after = ''
    browser_title = interview_status.question.interview.get_title().get('full', default_title)
    if not is_ajax:
        standard_header_start = standard_html_start(interview_language=interview_language, reload_after=reload_after, debug=DEBUG)
    if interview_status.question.question_type == "signature":
        extra_scripts.append('<script>$( document ).ready(function() {daInitializeSignature();});</script>')
        bodyclass="dasignature"
        if not is_ajax:
            #output = '<!doctype html>\n<html lang="' + interview_language + '">\n  <head>\n    <meta charset="utf-8">\n    <meta name="mobile-web-app-capable" content="yes">\n    <meta name="apple-mobile-web-app-capable" content="yes">\n    <meta http-equiv="X-UA-Compatible" content="IE=edge">\n    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0, user-scalable=0" />\n    <title>' + interview_status.question.interview.get_title().get('full', default_title) + '</title>\n    <link href="' + url_for('static', filename='app/signature.css') + '" rel="stylesheet">\n  </head>\n  <body class="dasignature">\n'
            start_output = standard_header_start + '\n    <title>' + browser_title + '</title>\n  </head>\n  <body class="dasignature">\n'
        output = signature_html(interview_status, DEBUG, ROOT, extra_scripts, validation_rules)
        if not is_ajax:
            end_output = scripts + "\n    " + "\n    ".join(extra_scripts) + """\n  </body>\n</html>"""
    else:
        bodyclass="dabody"
        if 'speak_text' in interview_status.extras and interview_status.extras['speak_text']:
            interview_status.initialize_screen_reader()
            util_language = docassemble.base.functions.get_language()
            util_dialect = docassemble.base.functions.get_dialect()
            question_language = interview_status.question.language
            if question_language != '*':
                the_language = question_language
            else:
                the_language = util_language
            if the_language == util_language and util_dialect is not None:
                the_dialect = util_dialect
            elif voicerss_config and 'languages' in voicerss_config and the_language in voicerss_config['languages']:
                the_dialect = voicerss_config['languages'][the_language]
            elif the_language in valid_voicerss_languages:
                the_dialect = valid_voicerss_languages[the_language][0]
            else:
                logmessage("Unable to determine dialect; reverting to default")
                the_language = DEFAULT_LANGUAGE
                the_dialect = DEFAULT_DIALECT
            for question_type in ['question', 'help']:
                for audio_format in ['mp3', 'ogg']:
                    interview_status.screen_reader_links[question_type].append([url_for('speak_file', question=interview_status.question.number, type=question_type, format=audio_format, language=the_language, dialect=the_dialect), audio_mimetype_table[audio_format]])
        # else:
        #     logmessage("speak_text was not here")
        content = as_html(interview_status, extra_scripts, extra_css, url_for, DEBUG, ROOT, validation_rules)
        if interview_status.using_screen_reader:
            for question_type in ['question', 'help']:
                #phrase = codecs.encode(to_text(interview_status.screen_reader_text[question_type]).encode('utf-8'), 'base64').decode().replace('\n', '')
                if question_type not in interview_status.screen_reader_text:
                    continue
                phrase = to_text(interview_status.screen_reader_text[question_type])
                #logmessage("Phrase is " + repr(phrase))
                if encrypted:
                    the_phrase = encrypt_phrase(phrase.encode('utf8'), secret)
                else:
                    the_phrase = pack_phrase(phrase)
                existing_entry = SpeakList.query.filter_by(filename=yaml_filename, key=user_code, question=interview_status.question.number, type=question_type, language=the_language, dialect=the_dialect).first()
                if existing_entry:
                    if existing_entry.encrypted:
                        existing_phrase = decrypt_phrase(existing_entry.phrase, secret)
                    else:
                        existing_phrase = unpack_phrase(existing_entry.phrase)
                    if phrase != existing_phrase:
                        logmessage("The phrase changed; updating it")
                        existing_entry.phrase = the_phrase
                        existing_entry.upload = None
                        existing_entry.encrypted = encrypted
                        db.session.commit()
                else:
                    new_entry = SpeakList(filename=yaml_filename, key=user_code, phrase=the_phrase, question=interview_status.question.number, type=question_type, language=the_language, dialect=the_dialect, encrypted=encrypted)
                    db.session.add(new_entry)
                    db.session.commit()
        # output = '<!DOCTYPE html>\n<html lang="' + interview_language + '">\n  <head>\n    <meta charset="utf-8">\n    <meta name="mobile-web-app-capable" content="yes">\n    <meta name="apple-mobile-web-app-capable" content="yes">\n    <meta http-equiv="X-UA-Compatible" content="IE=edge">\n    <meta name="viewport" content="width=device-width, initial-scale=1">\n    <link href="//maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css" rel="stylesheet">\n    <link href="//maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap-theme.min.css" rel="stylesheet">\n    <link href="//cdnjs.cloudflare.com/ajax/libs/jasny-bootstrap/3.1.3/css/jasny-bootstrap.min.css" rel="stylesheet">\n    <link href="' + url_for('static', filename='bootstrap-fileinput/css/fileinput.min.css') + '" media="all" rel="stylesheet" type="text/css" />\n    <link href="' + url_for('static', filename='jquery-labelauty/source/jquery-labelauty.css') + '" rel="stylesheet">\n    <link href="' + url_for('static', filename='app/app.css') + '" rel="stylesheet">'
        if not is_ajax:
            start_output = standard_header_start
            start_output += "".join(extra_css)
            start_output += '\n    <title>' + browser_title + '</title>\n  </head>\n  <body class="dabody">\n'
        output = make_navbar(interview_status, default_title, default_short_title, (steps - user_dict['_internal']['steps_offset']), SHOW_LOGIN, user_dict['_internal']['chat']) + flash_content + '    <div class="container">' + "\n      " + '<div class="row">\n        <div class="tab-content">\n'
        if interview_status.question.interview.use_progress_bar:
            output += progress_bar(user_dict['_internal']['progress'])
        output += content + "        </div>\n      </div>\n"
        if DEBUG:
            output += '      <div class="row">' + "\n"
            output += '        <div id="source" class="col-md-12 collapse">' + "\n"
            if interview_status.using_screen_reader:
                output += '          <h3>' + word('Plain text of sections') + '</h3>' + "\n"
                for question_type in ['question', 'help']:
                    if question_type in interview_status.screen_reader_text:
                        output += '<pre style="white-space: pre-wrap;">' + to_text(interview_status.screen_reader_text[question_type]) + '</pre>\n'
            output += '          <h3>' + word('Source code for question') + '</h3>' + "\n"
            if interview_status.question.source_code is None:
                output += word('unavailable')
            else:
                output += highlight(interview_status.question.source_code, YamlLexer(), HtmlFormatter())
            # if len(interview_status.question.fields_used):
            #     output += "<p>Variables set: " + ", ".join(['<code>' + obj + '</code>' for obj in sorted(interview_status.question.fields_used)]) + "</p>"
            # if len(interview_status.question.names_used):
            #     output += "<p>Variables in code: " + ", ".join(['<code>' + obj + '</code>' for obj in sorted(interview_status.question.names_used)]) + "</p>"
            # if len(interview_status.question.mako_names):
            #     output += "<p>Variables in templates: " + ", ".join(['<code>' + obj + '</code>' for obj in sorted(interview_status.question.mako_names)]) + "</p>"
            if len(interview_status.seeking) > 1:
                output += '          <h4>' + word('How question came to be asked') + '</h4>' + "\n"
                # output += '<ul>\n'
                # for foo in user_dict['_internal']['answered']:
                #     output += "<li>" + str(foo) + "</li>"
                # output += '</ul>\n'
                for stage in interview_status.seeking:
                    if 'question' in stage and 'reason' in stage and stage['question'] is not interview_status.question:
                        if stage['reason'] == 'initial':
                            output += "          <h5>" + word('Ran initial code') + "</h5>\n"
                        elif stage['reason'] == 'mandatory question':
                            output += "          <h5>" + word('Tried to ask mandatory question') + "</h5>\n"
                        elif stage['reason'] == 'mandatory code':
                            output += "          <h5>" + word('Tried to run mandatory code') + "</h5>\n"
                        elif stage['reason'] == 'asking':
                            output += "          <h5>" + word('Tried to ask question') + "</h5>\n"
                        if stage['question'].from_source.path != interview.source.path:
                            output += '          <p style="font-weight: bold;"><small>(' + word('from') + ' ' + stage['question'].from_source.path +")</small></p>\n"
                        if stage['question'].source_code is None:
                            output += word('unavailable')
                        else:
                            output += highlight(stage['question'].source_code, YamlLexer(), HtmlFormatter())
                        # if len(stage['question'].fields_used):
                        #     output += "<p>Variables set: " + ", ".join(['<code>' + obj + '</code>' for obj in sorted(stage['question'].fields_used)]) + "</p>"
                        # if len(stage['question'].names_used):
                        #     output += "<p>Variables in code: " + ", ".join(['<code>' + obj + '</code>' for obj in sorted(stage['question'].names_used)]) + "</p>"
                        # if len(stage['question'].mako_names):
                        #     output += "<p>Variables in templates: " + ", ".join(['<code>' + obj + '</code>' for obj in sorted(stage['question'].mako_names)]) + "</p>"
                    elif 'variable' in stage:
                        output += "          <h5>" + word('Needed definition of') + " <code>" + str(stage['variable']) + "</code></h5>\n"
                # output += '          <h4>' + word('Variables defined') + '</h4>' + "\n        <p>" + ", ".join(['<code>' + obj + '</code>' for obj in sorted(docassemble.base.functions.pickleable_objects(user_dict))]) + '</p>' + "\n"
            output += '        </div>' + "\n"
            output += '      </div>' + "\n"
        output += '    </div>'
        if not is_ajax:
            end_output = scripts + "\n    " + "".join(extra_scripts) + """\n  </body>\n</html>"""
    #logmessage(output.encode('utf8'))
    #logmessage("Request time interim: " + str(g.request_time()))
    if current_user.is_anonymous:
        the_user_id = 't' + str(session['tempuser'])
    else:
        the_user_id = current_user.id
    key = 'da:html:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:' + str(the_user_id)
    #logmessage("Setting " + key)
    pipe = r.pipeline()
    pipe.set(key, json.dumps(dict(body=output, extra_scripts=extra_scripts, extra_css=extra_css, browser_title=browser_title, lang=interview_language, bodyclass=bodyclass, reload_after=reload_after)))
    pipe.expire(key, 60)
    pipe.execute()
    #logmessage("Done setting " + key)
    if session.get('chatstatus', 'off') in ['waiting', 'standby', 'ringing', 'ready', 'on']:
        inputkey = 'da:input:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:' + str(the_user_id)
        r.publish(inputkey, json.dumps(dict(message='newpage', key=key)))
    if is_ajax:
        if 'reload_after' in interview_status.extras:
            reload_after = 1000 * int(interview_status.extras['reload_after'])
        else:
            reload_after = None
        response = jsonify(action='body', body=output, extra_scripts=extra_scripts, extra_css=extra_css, browser_title=browser_title, lang=interview_language, bodyclass=bodyclass, reload_after=reload_after, chat=user_dict['_internal']['chat'])
    else:
        output = start_output + output + end_output
        response = make_response(output.encode('utf8'), '200 OK')
        response.headers['Content-type'] = 'text/html; charset=utf-8'
    if set_cookie:
        response.set_cookie('secret', secret)
    if expire_visitor_secret:
        response.set_cookie('visitor_secret', '', expires=0)
    release_lock(user_code, yaml_filename)
    #logmessage("Request time final: " + str(g.request_time()))
    return response

if __name__ == "__main__":
    app.run()

def save_user_dict_key(user_code, filename):
    the_record = UserDictKeys.query.filter_by(key=user_code, filename=filename, user_id=current_user.id).first()
    if the_record:
        found = True
    else:
        found = False
    if not found:
        new_record = UserDictKeys(key=user_code, filename=filename, user_id=current_user.id)
        db.session.add(new_record)
        db.session.commit()
    return

def save_user_dict(user_code, user_dict, filename, secret=None, changed=False, encrypt=True, manual_user_id=None):
    nowtime = datetime.datetime.utcnow()
    user_dict['_internal']['modtime'] = nowtime
    if manual_user_id is not None or (current_user and current_user.is_authenticated and not current_user.is_anonymous):
        if manual_user_id is not None:
            the_user_id = manual_user_id
        else:
            the_user_id = current_user.id
        user_dict['_internal']['accesstime'][the_user_id] = nowtime
    else:
        user_dict['_internal']['accesstime'][-1] = nowtime
        the_user_id = None
    if changed is True:
        if encrypt:
            new_record = UserDict(modtime=nowtime, key=user_code, dictionary=encrypt_dictionary(user_dict, secret), filename=filename, user_id=the_user_id, encrypted=True)
        else:
            new_record = UserDict(modtime=nowtime, key=user_code, dictionary=pack_dictionary(user_dict), filename=filename, user_id=the_user_id, encrypted=False)
        db.session.add(new_record)
        db.session.commit()
    else:
        max_indexno = db.session.query(db.func.max(UserDict.indexno)).filter(UserDict.key == user_code and UserDict.filename == filename).scalar()
        if max_indexno is None:
            if encrypt:
                new_record = UserDict(modtime=nowtime, key=user_code, dictionary=encrypt_dictionary(user_dict, secret), filename=filename, user_id=the_user_id, encrypted=True)
            else:
                new_record = UserDict(modtime=nowtime, key=user_code, dictionary=pack_dictionary(user_dict), filename=filename, user_id=the_user_id, encrypted=False)
            db.session.add(new_record)
            db.session.commit()
        else:
            for record in UserDict.query.filter_by(key=user_code, filename=filename, indexno=max_indexno).all():
                if encrypt:
                    record.dictionary = encrypt_dictionary(user_dict, secret)
                    record.modtime = nowtime
                    record.encrypted = True
                else:
                    record.dictionary = pack_dictionary(user_dict)
                    record.modtime = nowtime
                    record.encrypted = False                   
            db.session.commit()
    return

def process_bracket_expression(match):
    #return("[" + repr(urllib.unquote(match.group(1)).encode('unicode_escape')) + "]")
    try:
        inner = codecs.decode(match.group(1), 'base64').decode('utf-8')
    except:
        inner = match.group(1)
    return("[" + repr(inner) + "]")

def myb64unquote(the_string):
    return(codecs.decode(the_string, 'base64').decode('utf-8'))

def safeid(text):
    return codecs.encode(text.encode('utf-8'), 'base64').decode().replace('\n', '')

def from_safeid(text):
    #logmessage("from_safeid: " + str(text))
    return(codecs.decode(text, 'base64').decode('utf-8'))

def progress_bar(progress):
    if progress == 0:
        return('');
    return('<div class="row"><div class="col-lg-6 col-md-8 col-sm-10"><div class="progress"><div class="progress-bar" role="progressbar" aria-valuenow="' + str(progress) + '" aria-valuemin="0" aria-valuemax="100" style="width: ' + str(progress) + '%;"></div></div></div></div>\n')

def get_unique_name(filename, secret):
    nowtime = datetime.datetime.utcnow()
    while True:
        newname = ''.join(random.choice(string.ascii_letters) for i in range(32))
        obtain_lock(newname, filename)
        existing_key = UserDict.query.filter_by(key=newname).first()
        if existing_key:
            release_lock(newname, filename)
            continue
        # cur = conn.cursor()
        # cur.execute("SELECT key from userdict where key=%s", [newname])
        # if cur.fetchone():
        #     #logmessage("Key already exists in database")
        #     continue
        new_user_dict = UserDict(modtime=nowtime, key=newname, filename=filename, dictionary=encrypt_dictionary(fresh_dictionary(), secret))
        db.session.add(new_user_dict)
        db.session.commit()
        # cur.execute("INSERT INTO userdict (key, filename, dictionary) values (%s, %s, %s);", [newname, filename, codecs.encode(pickle.dumps(initial_dict.copy()), 'base64').decode()])
        # conn.commit()
        return newname

# def update_user_id(the_user_code):
#     if current_user.id is not None and the_user_code is not None:
#         cur = conn.cursor()
#         cur.execute("UPDATE userdict set user_id=%s where key=%s", [current_user.id, the_user_code])
#         conn.commit()
#     return
    
def get_attachment_info(the_user_code, question_number, filename, secret):
    the_user_dict = None
    existing_entry = Attachments.query.filter_by(key=the_user_code, question=question_number, filename=filename).first()
    if existing_entry and existing_entry.dictionary:
        #the_user_dict = pickle.loads(codecs.decode(existing_entry.dictionary, 'base64'))
        if existing_entry.encrypted:
            the_user_dict = decrypt_dictionary(existing_entry.dictionary, secret)
        else:
            the_user_dict = unpack_dictionary(existing_entry.dictionary)
    # cur = conn.cursor()
    # cur.execute("select dictionary from attachments where key=%s and question=%s and filename=%s", [the_user_code, question_number, filename])
    # for d in cur:
    #     if d[0]:
    #         the_user_dict = pickle.loads(codecs.decode(d[0], 'base64'))
    #     break
    # conn.commit()
    return the_user_dict

def update_attachment_info(the_user_code, the_user_dict, the_interview_status, secret, encrypt=True):
    #logmessage("Got to update_attachment_info")
    Attachments.query.filter_by(key=the_user_code, question=the_interview_status.question.number, filename=the_interview_status.question.interview.source.path).delete()
    db.session.commit()
    if encrypt:
        new_attachment = Attachments(key=the_user_code, dictionary=encrypt_dictionary(the_user_dict, secret), question = the_interview_status.question.number, filename=the_interview_status.question.interview.source.path, encrypted=True)
    else:
        new_attachment = Attachments(key=the_user_code, dictionary=pack_dictionary(the_user_dict), question = the_interview_status.question.number, filename=the_interview_status.question.interview.source.path, encrypted=False)
    db.session.add(new_attachment)
    db.session.commit()
    return

def obtain_lock(user_code, filename):
    #logmessage("Obtain lock: " + str(user_code) + " " + str(filename))
    found = False
    count = 4
    while count > 0:
        record = UserDictLock.query.filter_by(key=user_code, filename=filename).first()
        if record:
            time.sleep(1.0)
        else:
            found = False
            break
        found = True
        count -= 1
    if found:
        release_lock(user_code, filename)
    new_record = UserDictLock(key=user_code, filename=filename)
    db.session.add(new_record)
    db.session.commit()
    
def release_lock(user_code, filename):
    #logmessage("Release lock: " + str(user_code) + " " + str(filename))
    UserDictLock.query.filter_by(key=user_code, filename=filename).delete()
    db.session.commit()


def make_navbar(status, page_title, page_short_title, steps, show_login, chat_info):
    navbar = """\
    <div class="navbar navbar-inverse navbar-fixed-top">
      <div class="container-fluid">
        <div class="navbar-header">
"""
    navbar += """\
          <button type="button" class="navbar-toggle collapsed mynavbar-toggle" data-toggle="collapse" data-target="#navbar-collapse">
            <span class="sr-only">Toggle navigation</span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
          </button>
"""
    if status.question.can_go_back and steps > 1:
        navbar += """\
          <span class="navbar-brand"><form style="inline-block" id="backbutton" method="POST"><input type="hidden" name="_back_one" value="1"><button class="dabackicon" type="submit"><i class="glyphicon glyphicon-chevron-left dalarge"></i></button></form></span>
"""
    navbar += """\
          <a href="#question" data-toggle="tab" class="navbar-brand"><span class="hidden-xs">""" + status.question.interview.get_title().get('full', page_title) + """</span><span class="visible-xs-block">""" + status.question.interview.get_title().get('short', page_short_title) + """</span></a>
          <a class="invisible" id="questionlabel" href="#question" data-toggle="tab">""" + word('Question') + """</a>
"""
    help_message = word("Help is available")
    extra_help_message = word("Help is available for this question")
    phone_message = word("Phone help is available")
    chat_message = word("Live chat is available")
    source_message = word("How this question came to be asked")
    if len(status.helpText):
        if status.question.helptext is None:
            navbar += '          <a title="' + help_message + '" class="mynavbar-text" href="#help" id="helptoggle" data-toggle="tab">' + word('Help') + '</a> <a title="' + phone_message + '" id="daPhoneAvailable" class="mynavbar-icon invisible" href="#help" data-toggle="tab"><i class="glyphicon glyphicon-earphone chat-active"></i></a> <a title="' + chat_message + '" id="daChatAvailable" class="mynavbar-icon invisible" href="#help" data-toggle="tab"><i class="glyphicon glyphicon-comment"></i></a>'
        else:
            navbar += '          <a title="' + extra_help_message + '" class="mynavbar-text daactivetext" href="#help" id="helptoggle" data-toggle="tab">' + word('Help') + ' <i class="glyphicon glyphicon-star"></i></a> <a title="' + phone_message + '" id="daPhoneAvailable" class="mynavbar-icon daactivetext invisible" href="#help" data-toggle="tab"><i class="glyphicon glyphicon-earphone chat-active"></i></a> <a title="' + chat_message + '" id="daChatAvailable" class="mynavbar-icon daactivetext invisible" href="#help" data-toggle="tab"><i class="glyphicon glyphicon-comment"></i></a>'
    elif chat_info['availability'] == 'available':
        navbar += '          <a title="' + phone_message + '" id="daPhoneAvailable" class="mynavbar-icon invisible" href="#help" data-toggle="tab"><i class="glyphicon glyphicon-earphone chat-active"></i></a> <a title="' + chat_message + '" id="daChatAvailable" class="mynavbar-icon invisible" href="#help" data-toggle="tab"><i class="glyphicon glyphicon-comment"></i></a>'
    navbar += """
        </div>
        <div class="collapse navbar-collapse" id="navbar-collapse">
          <ul class="nav navbar-nav navbar-left">
"""
    # if status.question.helptext is None:
    #     navbar += '<li><a href="#help" data-toggle="tab">' + word('Help') + "</a></li>\n"
    # else:
    #     navbar += '<li><a class="daactivetext" href="#help" data-toggle="tab">' + word('Help') + ' <i class="glyphicon glyphicon-star"></i>' + "</a></li>\n"
    if DEBUG:
        navbar += """\
            <li><a class="no-outline" title=""" + repr(str(source_message)) + """ id="sourcetoggle" href="#source" data-toggle="collapse" aria-expanded="false" aria-controls="source">""" + word('Source') + """</a></li>
"""
    navbar += """\
          </ul>
          <ul class="nav navbar-nav navbar-right">
"""
    if 'menu_items' in status.extras:
        if type(status.extras['menu_items']) is not list:
            custom_menu += '<li>' + word("Error: menu_items is not a Python list") + '</li>'
        elif len(status.extras['menu_items']):
            custom_menu = ""
            for menu_item in status.extras['menu_items']:
                if not (type(menu_item) is dict and 'url' in menu_item and 'label' in menu_item):
                    custom_menu += '<li>' + word("Error: menu item is not a Python dict with keys of url and label") + '</li>'
                else:
                    custom_menu += '<li><a href="' + menu_item['url'] + '">' + menu_item['label'] + '</a></li>'
        else:
            custom_menu = False
    else:
        custom_menu = False
    if show_login:
        if current_user.is_anonymous:
            #logmessage("is_anonymous is " + str(current_user.is_anonymous))
            if custom_menu:
                navbar += '            <li class="dropdown"><a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">' + word("Menu") + '<span class="caret"></span></a><ul class="dropdown-menu">' + custom_menu + '<li><a href="' + url_for('user.login', next=url_for('index')) + '">' + word('Sign in or sign up to save answers') + '</a></li></ul></li>' + "\n"
            else:
                navbar += '            <li><a href="' + url_for('user.login', next=url_for('index')) + '">' + word('Sign in or sign up to save answers') + '</a></li>' + "\n"
        else:
            navbar += '            <li class="dropdown"><a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">' + current_user.email + '<span class="caret"></span></a><ul class="dropdown-menu">'
            if custom_menu:
                navbar += custom_menu
            if current_user.has_role('admin', 'developer', 'advocate'):
                navbar +='<li><a href="' + url_for('monitor') + '">' + word('Monitor') + '</a></li>'
            if current_user.has_role('admin', 'developer'):
                navbar +='<li><a href="' + url_for('package_page') + '">' + word('Package Management') + '</a></li>'
                navbar +='<li><a href="' + url_for('logs') + '">' + word('Logs') + '</a></li>'
                navbar +='<li><a href="' + url_for('playground_page') + '">' + word('Playground') + '</a></li>'
                navbar +='<li><a href="' + url_for('utilities') + '">' + word('Utilities') + '</a></li>'
                if current_user.has_role('admin'):
                    navbar +='<li><a href="' + url_for('user_list') + '">' + word('User List') + '</a></li>'
                    navbar +='<li><a href="' + url_for('privilege_list') + '">' + word('Privileges List') + '</a></li>'
                    navbar +='<li><a href="' + url_for('config_page') + '">' + word('Configuration') + '</a></li>'
            navbar += '<li><a href="' + url_for('interview_list') + '">' + word('My Interviews') + '</a></li><li><a href="' + url_for('user_profile_page') + '">' + word('Profile') + '</a></li><li><a href="' + url_for('user.logout') + '">' + word('Sign out') + '</a></li></ul></li>'
    else:
        if custom_menu:
            navbar += '            <li class="dropdown"><a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">' + word("Menu") + '<span class="caret"></span></a><ul class="dropdown-menu">' + custom_menu + '<li><a href="' + url_for('exit') + '">' + word('Exit') + '</a></li></ul></li>' + "\n"
        else:
            navbar += '            <li><a href="' + url_for('exit') + '">' + word('Exit') + '</a></li>'
    navbar += """\
          </ul>
        </div>
      </div>
    </div>
"""
    return(navbar)

@app.context_processor
def utility_processor():
    def word(text):
        return docassemble.base.functions.word(text)
    def random_social():
        return 'local$' + ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    return dict(random_social=random_social, word=word)

def delete_session():
    for key in ['i', 'uid', 'key_logged', 'action', 'tempuser', 'user_id']:
        if key in session:
            del session[key]
    return

def reset_session(yaml_filename, secret):
    session['i'] = yaml_filename
    session['uid'] = get_unique_name(yaml_filename, secret)
    if 'key_logged' in session:
        del session['key_logged']
    if 'action' in session:
        del session['action']
    user_code = session['uid']
    #logmessage("User code is now " + str(user_code))
    user_dict = fresh_dictionary()
    return(user_code, user_dict)

def _endpoint_url(endpoint):
    url = url_for('index')
    if endpoint:
        url = url_for(endpoint)
    return url

@app.route('/speakfile', methods=['GET'])
def speak_file():
    audio_file = None
    filename = session['i']
    key = session['uid']
    encrypted = session.get('encrypted', False)
    question = request.args.get('question', None)
    question_type = request.args.get('type', None)
    file_format = request.args.get('format', None)
    the_language = request.args.get('language', None)
    the_dialect = request.args.get('dialect', None)
    secret = request.cookies.get('secret', None)
    if file_format not in ['mp3', 'ogg'] or not (filename and key and question and question_type and file_format and the_language and the_dialect):
        logmessage("Could not serve speak file because invalid or missing data was provided: filename " + str(filename) + " and key " + str(key) + " and question number " + str(question) + " and question type " + str(question_type) + " and language " + str(the_language) + " and dialect " + str(the_dialect))
        abort(404)
    entry = SpeakList.query.filter_by(filename=filename, key=key, question=question, type=question_type, language=the_language, dialect=the_dialect).first()
    if not entry:
        logmessage("Could not serve speak file because no entry could be found in speaklist for filename " + str(filename) + " and key " + str(key) + " and question number " + str(question) + " and question type " + str(question_type) + " and language " + str(the_language) + " and dialect " + str(the_dialect))
        abort(404)
    if not entry.upload:
        existing_entry = SpeakList.query.filter(SpeakList.phrase == entry.phrase, SpeakList.language == entry.language, SpeakList.dialect == entry.dialect, SpeakList.upload != None, SpeakList.encrypted == entry.encrypted).first()
        if existing_entry:
            logmessage("Found existing entry: " + str(existing_entry.id) + ".  Setting to " + str(existing_entry.upload))
            entry.upload = existing_entry.upload
            db.session.commit()
        else:
            if not VOICERSS_ENABLED:
                logmessage("Could not serve speak file because voicerss not enabled")
                abort(404)
            new_file_number = get_new_file_number(key, 'speak.mp3', yaml_file_name=filename)
            #phrase = codecs.decode(entry.phrase, 'base64')
            if entry.encrypted:
                phrase = decrypt_phrase(entry.phrase, secret)
            else:
                phrase = unpack_phrase(entry.phrase)
            url = "https://api.voicerss.org/"
            logmessage("Retrieving " + url)
            audio_file = SavedFile(new_file_number, extension='mp3', fix=True)
            audio_file.fetch_url_post(url, dict(key=voicerss_config['key'], src=phrase, hl=str(entry.language) + '-' + str(entry.dialect)))
            if audio_file.size_in_bytes() > 100:
                call_array = [daconfig.get('pacpl', 'pacpl'), '-t', 'ogg', audio_file.path + '.mp3']
                logmessage("Calling " + " ".join(call_array))
                result = call(call_array)
                if result != 0:
                    logmessage("Failed to convert downloaded mp3 (" + audio_file.path + '.mp3' + ") to ogg")
                    abort(404)
                entry.upload = new_file_number
                audio_file.finalize()
                db.session.commit()
            else:
                logmessage("Download from voicerss (" + url + ") failed")
                abort(404)
    if not entry.upload:
        logmessage("Upload file number was not set")
        abort(404)
    if not audio_file:
        audio_file = SavedFile(entry.upload, extension='mp3', fix=True)
    the_path = audio_file.path + '.' + file_format
    if not os.path.isfile(the_path):
        logmessage("Could not serve speak file because file (" + the_path + ") not found")
        abort(404)
    response = send_file(the_path, mimetype=audio_mimetype_table[file_format])
    return(response)

@app.route('/uploadedfile/<number>.<extension>', methods=['GET'])
def serve_uploaded_file_with_extension(number, extension):
    number = re.sub(r'[^0-9]', '', str(number))
    if S3_ENABLED:
        if not can_access_file_number(number):
            abort(404)
        the_file = SavedFile(number)
    else:
        file_info = get_info_from_file_number(number)
        if 'path' not in file_info:
            abort(404)
        else:
            if os.path.isfile(file_info['path'] + '.' + extension):
                extension, mimetype = get_ext_and_mimetype(file_info['path'] + '.' + extension)
                response = send_file(file_info['path'] + '.' + extension, mimetype=mimetype)
                return(response)
            else:
                abort(404)

@app.route('/uploadedfile/<number>', methods=['GET'])
def serve_uploaded_file(number):
    number = re.sub(r'[^0-9]', '', str(number))
    file_info = get_info_from_file_number(number)
    #file_info = get_info_from_file_reference(number)
    if 'path' not in file_info:
        abort(404)
    else:
        #block_size = 4096
        #status = '200 OK'
        response = send_file(file_info['path'], mimetype=file_info['mimetype'])
        return(response)

@app.route('/uploadedpage/<number>/<page>', methods=['GET'])
def serve_uploaded_page(number, page):
    number = re.sub(r'[^0-9]', '', str(number))
    page = re.sub(r'[^0-9]', '', str(page))
    file_info = get_info_from_file_number(number)
    if 'path' not in file_info:
        abort(404)
    else:
        filename = file_info['path'] + 'page-' + str(page) + '.png'
        if os.path.isfile(filename):
            response = send_file(filename, mimetype='image/png')
            return(response)
        else:
            abort(404)

@app.route('/uploadedpagescreen/<number>/<page>', methods=['GET'])
def serve_uploaded_pagescreen(number, page):
    number = re.sub(r'[^0-9]', '', str(number))
    page = re.sub(r'[^0-9]', '', str(page))
    file_info = get_info_from_file_number(number)
    if 'path' not in file_info:
        logmessage('no access to file number ' + str(number))
        abort(404)
    else:
        filename = file_info['path'] + 'screen-' + str(page) + '.png'
        if os.path.isfile(filename):
            response = send_file(filename, mimetype='image/png')
            return(response)
        else:
            logmessage('path ' + filename + ' is not a file')
            abort(404)

def user_can_edit_package(pkgname=None, giturl=None):
    if pkgname is not None:
        results = db.session.query(Package.id, PackageAuth.user_id, PackageAuth.authtype).outerjoin(PackageAuth, Package.id == PackageAuth.package_id).filter(Package.name == pkgname)
        if results.count() == 0:
            return(True)
        for d in results:
            if d.user_id == current_user.id:
                return True
    if giturl is not None:
        results = db.session.query(Package.id, PackageAuth.user_id, PackageAuth.authtype).outerjoin(PackageAuth, Package.id == PackageAuth.package_id).filter(Package.giturl == giturl)
        if results.count() == 0:
            return(True)
        for d in results:
            if d.user_id == current_user.id:
                return True
    return(False)

class Object(object):
    def __init__(self, **kwargs):
        for key, value in kwargs.iteritems():
            setattr(self, key, value)
    pass

@app.route('/visit_interview', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer', 'advocate'])
def visit_interview():
    i = request.args.get('i', None)
    uid = request.args.get('uid', None)
    userid = request.args.get('userid', None)
    key = 'da:session:uid:' + str(uid) + ':i:' + str(i) + ':userid:' + str(userid)
    try:
        obj = pickle.loads(r.get(key))
    except:
        abort(404)
    if 'secret' not in obj or 'encrypted' not in obj:
        abort(404)
    session['i'] = i
    session['uid'] = uid
    session['encrypted'] = obj['encrypted']
    if 'user_id' not in session:
        session['user_id'] = current_user.id
    session['key_logged'] = True
    if 'tempuser' in session:
        del session['tempuser']
    response = redirect(url_for('index'))
    response.set_cookie('visitor_secret', obj['secret'])
    return response

@app.route('/observer', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer', 'advocate'])
def observer():
    session['observer'] = 1
    i = request.args.get('i', None)
    uid = request.args.get('uid', None)
    userid = request.args.get('userid', None)
    observation_script = """
    <script>
      function daInitialize(){
        $(function () {
          $('[data-toggle="popover"]').popover({trigger: 'click focus', html: true})
        });
        $(".to-labelauty").labelauty({ width: "100%" });
        $(".to-labelauty-icon").labelauty({ label: false });
        $(function(){ 
          var navMain = $("#navbar-collapse");
          navMain.on("click", "a", null, function () {
            if (!($(this).hasClass("dropdown-toggle"))){
              navMain.collapse('hide');
            }
          });
          $("#helptoggle").on("click", function(){
            //console.log("Got to helptoggle");
            window.scrollTo(0, 0);
            $(this).removeClass('daactivetext')
            return true;
          });
          $("#sourcetoggle").on("click", function(){
            $(this).toggleClass("sourceactive");
          });
          $('#backToQuestion').click(function(event){
            event.preventDefault();
            $('#questionlabel').trigger('click');
          });
        });
        $(".showif").each(function(){
          var showIfSign = $(this).data('showif-sign');
          var showIfVar = $(this).data('showif-var');
          var showIfVarEscaped = showIfVar.replace(/(:|\.|\[|\]|,|=)/, "\\\\$1");
          var showIfVal = $(this).data('showif-val');
          var saveAs = $(this).data('saveas');
          var isSame = (saveAs == showIfVar);
          var showIfDiv = this;
          var showHideDiv = function(){
            //console.log("showHideDiv1")
            if($(this).parents(".showif").length !== 0){
              return;
            }
            var theVal;
            if ($(this).attr('type') == "checkbox" || $(this).attr('type') == "radio"){
              theVal = $("input[name='" + showIfVarEscaped + "']:checked").val();
            }
            else{
              theVal = $(this).val();
            }
            //console.log("val is " + theVal + " and showIfVal is " + showIfVal)
            if(theVal == showIfVal){
              //console.log("They are the same");
              if (showIfSign){
                $(showIfDiv).removeClass("invisible");
                $(showIfDiv).find('input, textarea, select').prop("disabled", false);
              }
              else{
                $(showIfDiv).addClass("invisible");
                $(showIfDiv).find('input, textarea, select').prop("disabled", true);
              }
            }
            else{
              //console.log("They are not the same");
              if (showIfSign){
                $(showIfDiv).addClass("invisible");
                $(showIfDiv).find('input, textarea, select').prop("disabled", true);
              }
              else{
                $(showIfDiv).removeClass("invisible");
                $(showIfDiv).find('input, textarea, select').prop("disabled", false);
              }
            }
          };
          $("#" + showIfVarEscaped).each(showHideDiv);
          $("#" + showIfVarEscaped).change(showHideDiv);
          $("input[type='radio'][name='" + showIfVarEscaped + "']").each(showHideDiv);
          $("input[type='radio'][name='" + showIfVarEscaped + "']").change(showHideDiv);
          $("input[type='checkbox'][name='" + showIfVarEscaped + "']").each(showHideDiv);
          $("input[type='checkbox'][name='" + showIfVarEscaped + "']").change(showHideDiv);
        });
        dadisable = setTimeout(function(){
          $("#daform").find('button[type="submit"]').prop("disabled", true);
          //$("#daform").find(':input').prop("disabled", true);
        }, 1);
      }
      $( document ).ready(function(){
        daInitialize();
        if (location.protocol === 'http:' || document.location.protocol === 'http:'){
            socket = io.connect("http://" + document.domain + "/observer" + location.port, {path: '/ws/socket.io'});
        }
        if (location.protocol === 'https:' || document.location.protocol === 'https:'){
            socket = io.connect("https://" + document.domain + "/observer" + location.port, {path: '/wss/socket.io'});
        }
        if (typeof socket !== 'undefined') {
            socket.on('connect', function() {
                //console.log("Connected!");
                socket.emit('observe', {uid: """ + repr(str(uid)) + """, i: """ + repr(str(i)) + """, userid: """ + repr(str(userid)) + """});
            });
            socket.on('terminate', function() {
                //console.log("Terminating socket");
                socket.disconnect();
            });
            socket.on('disconnect', function() {
                //console.log("Disconnected socket");
                //socket = null;
            });
            socket.on('newpage', function(incoming) {
                var data = incoming.obj;
                $("body").html(data.body);
                $("body").removeClass();
                $("body").addClass(data.bodyclass);
                daInitialize();
                var tempDiv = document.createElement('div');
                tempDiv.innerHTML = data.extra_scripts;
                var scripts = tempDiv.getElementsByTagName('script');
                for (var i = 0; i < scripts.length; i++){
                  eval(scripts[i].innerHTML);
                }
                for (var i = 0; i < data.extra_css.length; i++){
                  $("head").append(data.extra_css[i]);
                }
                document.title = data.browser_title;
                if ($("html").attr("lang") != data.lang){
                  $("html").attr("lang", data.lang);
                }
            });
            socket.on('pushchanges', function(data) {
                var valArray = Object();
                var values = data.parameters;
                for (var i = 0; i < values.length; i++) {
                    valArray[values[i].name] = values[i].value;
                }
                $("#daform").each(function(){
                    $(this).find(':input').each(function(){
                        var type = $(this).attr('type');
                        var id = $(this).attr('id');
                        var name = $(this).attr('name');
                        if (type == 'checkbox'){
                            if (name in valArray){
                                if (valArray[name] == 'True'){
                                    $(this).prop('checked', true);
                                }
                                else{
                                    $(this).prop('checked', false);
                                }
                            }
                            else{
                                $(this).prop('checked', false);
                            }
                        }
                        else if (type == 'radio'){
                            if (name in valArray){
                                if (valArray[name] == $(this).val()){
                                    $(this).prop('checked', true);
                                }
                                else{
                                    $(this).prop('checked', false);
                                }
                            }
                        }
                        else if ($(this).data().hasOwnProperty('sliderMax')){
                            $(this).slider('setValue', parseInt(valArray[name]));
                        }
                        else{
                            if (name in valArray){
                                $(this).val(valArray[name]);
                            }
                        }
                    });
                });
            });
        }
    });
    </script>
"""
    the_key = 'da:html:uid:' + str(uid) + ':i:' + str(i) + ':userid:' + str(userid)
    html = r.get(the_key)
    if html is not None:
        obj = json.loads(html)
    else:
        logmessage("Failed to load JSON from key " + the_key)
        obj = dict()
    output = standard_html_start(interview_language=obj.get('lang', 'en'), debug=DEBUG)
    output += "".join(obj.get('extra_css', list()))
    output += '\n    <title>' + word('Observation') + '</title>\n  </head>\n  <body class="' + obj.get('bodyclass', 'dabody') + '">\n'
    output += obj.get('body', '')
    output += standard_scripts() + observation_script + "\n    " + "".join(obj.get('extra_scripts', list())) + "\n  </body>\n</html>"
    response = make_response(output.encode('utf8'), '200 OK')
    response.headers['Content-type'] = 'text/html; charset=utf-8'
    return response

@app.route('/monitor', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer', 'advocate'])
def monitor():
    session['monitor'] = 1
    if 'user_id' not in session:
        session['user_id'] = current_user.id
    phone_number_key = 'da:monitor:phonenumber:' + str(session['user_id'])
    default_phone_number = r.get(phone_number_key)
    if default_phone_number is None:
        default_phone_number = ''
    sub_role_key = 'da:monitor:userrole:' + str(session['user_id'])
    if r.exists(sub_role_key):
        subscribed_roles = r.hgetall(sub_role_key)
        r.expire(sub_role_key, 2592000)
    else:
        subscribed_roles = dict()
    key = 'da:monitor:available:' + str(current_user.id)
    if r.exists(key):
        daAvailableForChat = 'true'
    else:
        daAvailableForChat = 'false'
    call_forwarding_on = 'false'
    if twilio_config is not None:
        forwarding_phone_number = twilio_config['name']['default'].get('number', None)
        if forwarding_phone_number is not None:
            call_forwarding_on = 'true'
    script = '<script type="text/javascript" src="' + url_for('static', filename='app/socket.io.min.js') + '"></script>\n' + """<script type="text/javascript" charset="utf-8">
    var daAudioContext = null;
    var socket;
    var soundBuffer = Object();
    var daShowingNotif = false;
    var daUpdatedSessions = Object();
    var daUserid = """ + str(current_user.id) + """;
    var daPhoneOnMessage = """ + repr(str("The user can call you.  Click to cancel.")) + """;
    var daPhoneOffMessage = """ + repr(str("Click if you want the user to be able to call you.")) + """;
    var daSessions = Object();
    var daAvailRoles = Object();
    var daChatPartners = Object();
    var daPhonePartners = Object();
    var daNewPhonePartners = Object();
    var daTermPhonePartners = Object();
    var daUsePhone = """ + call_forwarding_on + """;
    var daSubscribedRoles = """ + json.dumps(subscribed_roles) + """;
    var daAvailableForChat = """ + daAvailableForChat + """;
    var daPhoneNumber = """ + repr(str(default_phone_number)) + """;
    var daFirstTime = 1;
    var updateMonitorInterval = null;
    var daNotificationsEnabled = false;
    function daOnError(){
        console.log('daOnError');
    }
    function loadSoundBuffer(key, url_a, url_b){
        var pos = 0;
        if (daAudioContext == null){
            return;
        }
        var request = new XMLHttpRequest();
        request.open('GET', url_a, true);
        request.responseType = 'arraybuffer';
        request.onload = function(){
            daAudioContext.decodeAudioData(request.response, function(buffer){
                if (!buffer){
                    if (pos == 1){
                        console.error('error decoding file data');
                        return;
                    }
                    else {
                        pos = 1;
                        console.info('error decoding file data, trying next source');
                        request.open("GET", url_b, true);
                        return request.send();
                    }
                }
                soundBuffer[key] = buffer;
            },
            function(error){
                if (pos == 1){
                    console.error('decodeAudioData error');
                    return;
                }
                else{
                    pos = 1;
                    console.info('decodeAudioData error, trying next source');
                    request.open("GET", url_b, true);
                    return request.send();
                }
            });
        }
        request.send();
    }
    function playSound(key) {
        var buffer = soundBuffer[key];
        if (!daAudioContext || !buffer){
            return;
        }
        var source = daAudioContext.createBufferSource();
        source.buffer = buffer;
        source.connect(daAudioContext.destination);
        source.start(0);
    }
    function checkNotifications(){
        if (daNotificationsEnabled){
            return;
        }
        if (!("Notification" in window)) {
            daNotificationsEnabled = false;
            return;
        }
        if (Notification.permission === "granted") {
            daNotificationsEnabled = true;
            return;
        }
        if (Notification.permission !== 'denied') {
            Notification.requestPermission(function (permission) {
                if (permission === "granted") {
                    daNotificationsEnabled = true;
                }
            });
        }
    }
    function notifyOperator(key, mode, message) {
        var skey = key.replace(/(:|\.|\[|\]|,|=|\/)/g, '\\\\$1');
        if (mode == "chat"){
          playSound('newmessage');
        }
        else{
          playSound('newconversation');
        }
        if ($("#listelement" + skey).offset().top > $(window).scrollTop() + $(window).height()){
          if (mode == "chat"){
            $("#chat-message-below").html("New message below");
          }
          else{
            $("#chat-message-below").html("New conversation below");
          }
          //$("#chat-message-below").data('key', key);
          $("#chat-message-below").slideDown();
          daShowingNotif = true;
          markAsUpdated(key);
        }
        else if ($("#listelement" + skey).offset().top + $("#listelement" + skey).height() < $(window).scrollTop() + 32){
          if (mode == "chat"){
            $("#chat-message-above").html(""" + repr(str(word("New message above"))) + """);
          }
          else{
            $("#chat-message-above").html(""" + repr(str(word("New conversation above"))) + """);
          }
          //$("#chat-message-above").data('key', key);
          $("#chat-message-above").slideDown();
          daShowingNotif = true;
          markAsUpdated(key);
        }
        else{
          //console.log("It is visible");
        }
        if (!daNotificationsEnabled){
            //console.log("Browser will not enable notifications")
            return;
        }
        if (!("Notification" in window)) {
            return;
        }
        if (Notification.permission === "granted") {
            var notification = new Notification(message);
        }
        else if (Notification.permission !== 'denied') {
            Notification.requestPermission(function (permission) {
                if (permission === "granted") {
                    var notification = new Notification(message);
                    daNotificationsEnabled = true;
                }
            });
        }
    }
    function phoneNumberOk(){
        var phoneNumber = $("#daPhoneNumber").val();
        if (phoneNumber == '' || phoneNumber.match(/^\+?[1-9]\d{1,14}$/)){
            return true;
        }
        else{
            return false;
        }
    }
    function checkPhone(){
        //console.log("Doing checkPhone");
        $("#daPhoneNumber").val($("#daPhoneNumber").val().replace(/[^0-9\+]/g, ''));
        var the_number = $("#daPhoneNumber").val();
        if (the_number[0] != '+'){
            $("#daPhoneNumber").val('+' + the_number);
        }
        if (phoneNumberOk()){
            $("#daPhoneNumber").parent().removeClass("has-error");
            $("#daPhoneError").addClass("invisible");
            daPhoneNumber = $("#daPhoneNumber").val();
            if (daPhoneNumber == ''){
                daPhoneNumber = null;
            }
            else{
                $(".phone").removeClass("invisible");
            }
        }
        else{
            $("#daPhoneNumber").parent().addClass("has-error");
            $("#daPhoneError").removeClass("invisible");
            daPhoneNumber = null;
            $(".phone").addClass("invisible");
        }
        $("#daPhoneSaved").removeClass("invisible");
        setTimeout(function(){
            $("#daPhoneSaved").addClass("invisible");
        }, 2000);
    }
    function allSessions(uid, yaml_filename){
        var prefix = 'da:session:uid:' + uid + ':i:' + yaml_filename + ':userid:';
        var output = Array();
        for (var key in daSessions){
            if (daSessions.hasOwnProperty(key) && key.indexOf(prefix) == 0){
                output.push(key);
            }
        }
        return(output);
    }
    function scrollChat(key){
        var chatScroller = $(key).find('ul').first();
        if (chatScroller.length){
            var height = chatScroller[0].scrollHeight;
            chatScroller.animate({scrollTop: height}, 800);
        }
        else{
            console.log("scrollChat: error")
        }
    }
    function scrollChatFast(key){
        var chatScroller = $(key).find('ul').first();
        if (chatScroller.length){
          var height = chatScroller[0].scrollHeight;
            //console.log("Scrolling to " + height + " where there are " + chatScroller[0].childElementCount + " children");
            chatScroller.scrollTop(height);
          }
        else{
            console.log("scrollChatFast: error")
        }
    }
    function do_update_monitor(){
        //console.log("do update monitor with " + daAvailableForChat);
        if (phoneNumberOk()){
          daPhoneNumber = $("#daPhoneNumber").val();
          if (daPhoneNumber == ''){
            daPhoneNumber = null;
          }
        }
        else{
          daPhoneNumber = null;
        }
        socket.emit('updatemonitor', {available_for_chat: daAvailableForChat, phone_number: daPhoneNumber, subscribed_roles: daSubscribedRoles, phone_partners_to_add: daNewPhonePartners, phone_partners_to_terminate: daTermPhonePartners});
    }
    function update_monitor(){
        if (updateMonitorInterval != null){
            clearInterval(updateMonitorInterval);
        }
        do_update_monitor();
        updateMonitorInterval = setInterval(do_update_monitor, 6000);
        //console.log("update_monitor");
    }
    function isHidden(ref){
        if (($(ref).offset().top + $(ref).height() < $(window).scrollTop() + 32)){
            return -1;
        }
        else if ($(ref).offset().top > $(window).scrollTop() + $(window).height()){
            return 1;
        }
        else{
            return 0;
        }
    }
    function markAsUpdated(key){
        var skey = key.replace(/(:|\.|\[|\]|,|=|\/)/g, '\\\\$1');
        if (isHidden("#listelement" + skey)){
            daUpdatedSessions["#listelement" + skey] = 1;
        }
    }
    function activateChatArea(key){
        var skey = key.replace(/(:|\.|\[|\]|,|=|\/)/g, '\\\\$1');
        $("#listelement" + skey).addClass("new-message");
        markAsUpdated(key);
        $("#chatarea" + skey).removeClass('invisible');
        $("#chatarea" + skey).find('input, button').prop("disabled", false);
        $("#chatarea" + skey).find('ul').html('');
        socket.emit('chat_log', {key: key});
    }
    function deActivateChatArea(key){
        var skey = key.replace(/(:|\.|\[|\]|,|=|\/)/g, '\\\\$1');
        $("#chatarea" + skey).find('input, button').prop("disabled", true);
        $("#listelement" + skey).removeClass("new-message");
    }
    function undraw_session(key){
        //console.log("Undrawing...")
        var skey = key.replace(/(:|\.|\[|\]|,|=|\/)/g, '\\\\$1');
        var xButton = document.createElement('a');
        var xButtonIcon = document.createElement('i');
        $(xButton).addClass("corner-remove");
        $(xButtonIcon).addClass("glyphicon glyphicon-remove-circle");
        $(xButtonIcon).appendTo($(xButton));
        $("#listelement" + skey).addClass("list-group-item-danger");
        $("#session" + skey).find("a").remove();
        $("#session" + skey).find("span").first().html('""" + word("offline") + """');
        $("#session" + skey).find("span").first().removeClass('label-info');
        $("#session" + skey).find("span").first().addClass('label-danger');
        $(xButton).click(function(){
            $("#listelement" + skey).slideUp(300, function(){
                $("#listelement" + skey).remove();
                check_if_empty();
            });
        });
        $(xButton).appendTo($("#session" + skey));
        $("#iframe" + skey).find('iframe').first().contents().find('body').addClass("dainactive");
        $("#chatarea" + skey).find('input, button').prop("disabled", true);
        delete daSessions[key];
    }
    function publish_chat_log(uid, yaml_filename, userid, mode, messages){
        var keys; 
        //if (mode == 'peer' || mode == 'peerhelp'){
        //    keys = allSessions(uid, yaml_filename);
        //}
        //else{
            keys = ['da:session:uid:' + uid + ':i:' + yaml_filename + ':userid:' + userid];
        //}
        for (var i = 0; i < keys.length; ++i){
            key = keys[i];
            var skey = key.replace(/(:|\.|\[|\]|,|=|\/)/g, '\\\\$1');
            var chatArea = $("#chatarea" + skey).find('ul').first();
            for (var i = 0; i < messages.length; ++i){
                var message = messages[i];
                var newLi = document.createElement('li');
                $(newLi).addClass("list-group-item");
                if (message.is_self){
                    $(newLi).addClass("list-group-item-warning dalistright");
                }
                else{
                    $(newLi).addClass("list-group-item-info");
                }
                $(newLi).html(message.message);
                $(newLi).appendTo(chatArea);
            }
            scrollChatFast("#chatarea" + skey);
        }
    }
    function check_if_empty(){
        if ($("#monitorsessions").find("li").length > 0){
            $("#emptylist").addClass("invisible");
        }
        else{
            $("#emptylist").removeClass("invisible");
        }
    }
    function draw_session(key, obj){
        var skey = key.replace(/(:|\.|\[|\]|,|=|\/)/g, '\\\\$1');
        var the_html;
        var wants_to_chat;
        if (obj.chatstatus == 'waiting' || obj.chatstatus == 'standby' || obj.chatstatus == 'ringing' || obj.chatstatus == 'ready' || obj.chatstatus == 'on'){
            wants_to_chat = true;
        }
        if (wants_to_chat){
            the_html = obj.browser_title + ' &mdash; '
            if (obj.hasOwnProperty('first_name')){
              the_html += obj.first_name + ' ' + obj.last_name;
            }
            else{
              the_html += '""" + word("anonymous visitor") + """ ' + obj.temp_user_id;
            }
        }
        var theListElement;
        var sessionDiv;
        var theIframeContainer;
        var theChatArea;
        if ($("#session" + skey).length && !(key in daSessions)){
            $("#listelement" + skey).removeClass("list-group-item-danger");
            $("#iframe" + skey).find('iframe').first().contents().find('body').removeClass("dainactive");
        }
        daSessions[key] = 1;
        if ($("#session" + skey).length){
            theListElement = $("#listelement" + skey).first();
            sessionDiv = $("#session" + skey).first();
            //controlDiv = $("#control" + skey).first();
            theIframeContainer = $("#iframe" + skey).first();
            theChatArea = $("#chatarea" + skey).first();
            $(sessionDiv).empty();
            if (obj.chatstatus == 'on' && key in daChatPartners && $("#chatarea" + skey).find('button').first().prop("disabled") == true){
                activateChatArea(key);
            }
        }
        else{
            var theListElement = document.createElement('li');
            $(theListElement).addClass('list-group-item');
            $(theListElement).attr('id', "listelement" + key);
            var sessionDiv = document.createElement('div');
            $(sessionDiv).attr('id', "session" + key);
            $(sessionDiv).addClass('chat-session');
            $(sessionDiv).appendTo($(theListElement));
            $(theListElement).appendTo("#monitorsessions");
            // controlDiv = document.createElement('div');
            // $(controlDiv).attr('id', "control" + key);
            // $(controlDiv).addClass("chatcontrol invisible chat-session");
            // $(controlDiv).appendTo($(theListElement));
            theIframeContainer = document.createElement('div');
            $(theIframeContainer).addClass("observer-container invisible");
            $(theIframeContainer).attr('id', 'iframe' + key);
            var theIframe = document.createElement('iframe');
            $(theIframe).addClass("observer");
            $(theIframe).attr('name', 'iframe' + key);
            $(theIframe).appendTo($(theIframeContainer));
            $(theIframeContainer).appendTo($(theListElement));
            var theChatArea = document.createElement('div');
            $(theChatArea).addClass('monitor-chat-area invisible');
            $(theChatArea).html('<div class="row"><div class="col-md-12"><ul class="list-group dachatbox" id="daCorrespondence"></ul></div></div><form autocomplete="off"><div class="row"><div class="col-md-12"><div class="input-group"><input type="text" class="form-control" disabled><span class="input-group-btn"><button class="btn btn-default" type="button" disabled>""" + word("Send") + """</button></span></div></div></div></form>');
            $(theChatArea).attr('id', 'chatarea' + key);
            var submitter = function(){
                //console.log("I am the submitter and I am submitting " + key);
                var input = $(theChatArea).find("input").first();
                var message = input.val().trim();
                if (message == null || message == ""){
                    //console.log("Message was blank");
                    return false;
                }
                socket.emit('chatmessage', {key: key, data: input.val()});
                input.val('');
                return false;
            };
            $(theChatArea).find("button").click(submitter);
            $(theChatArea).find("input").bind('keypress keydown keyup', function(e){
                if(e.keyCode == 13) { submitter(); e.preventDefault(); }
            });
            $(theChatArea).find("input").focus(function(){
              $(theListElement).removeClass("new-message");
            });
            $(theChatArea).appendTo($(theListElement));
            if (obj.chatstatus == 'on' && key in daChatPartners){
                activateChatArea(key);
            }
        }
        var theText = document.createElement('span');
        $(theText).addClass('chat-title-label');
        theText.innerHTML = the_html;
        var statusLabel = document.createElement('span');
        $(statusLabel).addClass("label label-info chat-status-label");
        $(statusLabel).html(obj.chatstatus);
        $(statusLabel).appendTo($(sessionDiv));
        if (daUsePhone){
          var phoneButton = document.createElement('a');
          var phoneIcon = document.createElement('i');
          $(phoneIcon).addClass("glyphicon glyphicon-earphone");
          $(phoneIcon).appendTo($(phoneButton));
          $(phoneButton).addClass("label phone");
          if (key in daPhonePartners){
            $(phoneButton).addClass("phone-on label-success");
            $(phoneButton).attr('title', daPhoneOnMessage);
          }
          else{
            $(phoneButton).addClass("phone-off label-default");
            $(phoneButton).attr('title', daPhoneOffMessage);
          }
          $(phoneButton).addClass('observebutton')
          $(phoneButton).appendTo($(sessionDiv));
          $(phoneButton).attr('href', '#');
          if (daPhoneNumber == null){
            $(phoneButton).addClass("invisible");
          }
          $(phoneButton).click(function(e){
            if ($(this).hasClass("phone-off") && daPhoneNumber != null){
              $(this).removeClass("phone-off");
              $(this).removeClass("label-default");
              $(this).addClass("phone-on");
              $(this).addClass("label-success");
              $(this).attr('title', daPhoneOnMessage);
              daPhonePartners[key] = 1;
              daNewPhonePartners[key] = 1;
              if (key in daTermPhonePartners){
                delete daTermPhonePartners[key];
              }
              update_monitor();
            }
            else{
              $(this).removeClass("phone-on");
              $(this).removeClass("label-success");
              $(this).addClass("phone-off");
              $(this).addClass("label-default");
              $(this).attr('title', daPhoneOffMessage);
              if (key in daPhonePartners){
                delete daPhonePartners[key];
              }
              if (key in daNewPhonePartners){
                delete daNewPhonePartners[key];
              }
              daTermPhonePartners[key] = 1;
              update_monitor();
            }
            e.preventDefault();
            return false;
          });
        }
        var unblockButton = document.createElement('a');
        $(unblockButton).addClass("label label-info observebutton");
        if (!obj.blocked){
            $(unblockButton).addClass("invisible");
        }
        $(unblockButton).html('""" + word("Unblock") + """');
        $(unblockButton).attr('href', '#');
        $(unblockButton).appendTo($(sessionDiv));
        var blockButton = document.createElement('a');
        $(blockButton).addClass("label label-danger observebutton");
        if (obj.blocked){
            $(blockButton).addClass("invisible");
        }
        $(blockButton).html('""" + word("Block") + """');
        $(blockButton).attr('href', '#');
        $(blockButton).appendTo($(sessionDiv));
        $(blockButton).click(function(e){
            $(unblockButton).removeClass("invisible");
            $(this).addClass("invisible");
            deActivateChatArea(key);
            socket.emit('block', {key: key});
            e.preventDefault();
            return false;
        });
        $(unblockButton).click(function(e){
            $(blockButton).removeClass("invisible");
            $(this).addClass("invisible");
            socket.emit('unblock', {key: key});
            e.preventDefault();
            return false;
        });
        var joinButton = document.createElement('a');
        $(joinButton).addClass("label label-warning observebutton");
        $(joinButton).html('""" + word("Join") + """');
        $(joinButton).attr('href', '""" + url_for('visit_interview') + """?' + $.param({i: obj.i, uid: obj.uid, userid: obj.userid}));
        $(joinButton).attr('target', '_blank');
        $(joinButton).appendTo($(sessionDiv));
        if (wants_to_chat){
            var openButton = document.createElement('a');
            $(openButton).addClass("label label-primary observebutton");
            $(openButton).attr('href', '""" + url_for('observer') + """?' + $.param({i: obj.i, uid: obj.uid, userid: obj.userid}));
            //$(openButton).attr('href', 'about:blank');
            $(openButton).attr('id', 'observe' + key);
            $(openButton).attr('target', 'iframe' + key);
            $(openButton).html('""" + word("Observe") + """');
            $(openButton).appendTo($(sessionDiv));
            var controlButton = document.createElement('a');
            $(controlButton).addClass("label label-default observebutton invisible");
            $(controlButton).html('""" + word("Stop Observing") + """');
            $(controlButton).attr('href', '#');
            $(controlButton).appendTo($(sessionDiv));
            $(openButton).click(function(){
                //console.log("Observing..");
                $(this).addClass("invisible");
                $(controlButton).removeClass("invisible");
                $("#iframe" + skey).removeClass("invisible");
                return true;
            });
            $(controlButton).click(function(e){
                //console.log("Unobserving..");
                $(this).addClass("invisible");
                $(openButton).removeClass("invisible");
                var theIframe = $("#iframe" + skey).find('iframe');
                if (theIframe != null && theIframe.contentWindow){
                    theIframe.contentWindow.document.open();
                    theIframe.contentWindow.document.write("");
                    theIframe.contentWindow.document.close();
                }
                $("#iframe" + skey).slideUp(400, function(){
                    $(this).css("display", "").addClass("invisible");
                });
                e.preventDefault();
                return false;
            });
            if ($(theIframeContainer).hasClass("invisible")){
                $(openButton).removeClass("invisible");
                $(controlButton).addClass("invisible");
            }
            else{
                $(openButton).addClass("invisible");
                $(controlButton).removeClass("invisible");
            }
        }
        $(theText).appendTo($(sessionDiv));
        if (obj.chatstatus == 'on' && key in daChatPartners && $("#chatarea" + skey).hasClass('invisible')){
            activateChatArea(key);
        }
        if ((obj.chatstatus != 'on' || !(key in daChatPartners)) && $("#chatarea" + skey).find('button').first().prop("disabled") == false){
            deActivateChatArea(key);
        }
        else if (obj.blocked){
            deActivateChatArea(key);
        }
    }
    $(document).ready(function(){
        try {
            window.AudioContext = window.AudioContext || window.webkitAudioContext;
            daAudioContext = new AudioContext();
        }
        catch(e) {
            console.log('Web Audio API is not supported in this browser');
        }
        loadSoundBuffer('newmessage', '""" + url_for('static', filename='sounds/notification-click-on.mp3') + """', '""" + url_for('static', filename='sounds/notification-click-on.ogg') + """');
        loadSoundBuffer('newconversation', '""" + url_for('static', filename='sounds/notification-stapler.mp3') + """', '""" + url_for('static', filename='sounds/notification-stapler.ogg') + """');
        loadSoundBuffer('signinout', '""" + url_for('static', filename='sounds/notification-snap.mp3') + """', '""" + url_for('static', filename='sounds/notification-snap.ogg') + """');
        if (location.protocol === 'http:' || document.location.protocol === 'http:'){
            socket = io.connect("http://" + document.domain + "/monitor" + location.port, {path: '/ws/socket.io'});
        }
        if (location.protocol === 'https:' || document.location.protocol === 'https:'){
            socket = io.connect("https://" + document.domain + "/monitor" + location.port, {path: '/wss/socket.io'});
        }
        if (typeof socket !== 'undefined') {
            socket.on('connect', function() {
                //console.log("Connected!");
                update_monitor();
            });
            socket.on('terminate', function() {
                //console.log("Terminating socket");
                socket.disconnect();
            });
            socket.on('disconnect', function() {
                //console.log("Disconnected socket");
                //socket = null;
            });
            socket.on('refreshsessions', function(data) {
                update_monitor();
            });
            socket.on('chatready', function(data) {
                var key = 'da:session:uid:' + data.uid + ':i:' + data.i + ':userid:' + data.userid
                //console.log('chatready: ' + key);
                activateChatArea(key);
                notifyOperator(key, "chatready", """ + repr(str(word("New chat connection from "))) + """ + data.name)
            });
            socket.on('chatstop', function(data) {
                var key = 'da:session:uid:' + data.uid + ':i:' + data.i + ':userid:' + data.userid
                //console.log('chatstop: ' + key);
                if (key in daChatPartners){
                    delete daChatPartners[key];
                }
                deActivateChatArea(key);
            });
            socket.on('chat_log', function(arg) {
                publish_chat_log(arg.uid, arg.i, arg.userid, arg.mode, arg.data);
            });            
            socket.on('block', function(arg) {
                //console.log("back from blocking " + arg.key);
                update_monitor();
            });            
            socket.on('unblock', function(arg) {
                //console.log("back from unblocking " + arg.key);
                update_monitor();
            });            
            socket.on('chatmessage', function(data) {
                var keys; 
                if (data.data.mode == 'peer' || data.data.mode == 'peerhelp'){
                  keys = allSessions(data.uid, data.i);
                }
                else{
                  keys = ['da:session:uid:' + data.uid + ':i:' + data.i + ':userid:' + data.userid];
                }
                for (var i = 0; i < keys.length; ++i){
                  key = keys[i];
                  var skey = key.replace(/(:|\.|\[|\]|,|=|\/)/g, '\\\\$1');
                  //console.log("Received chat message for #chatarea" + skey);
                  var chatArea = $("#chatarea" + skey).find('ul').first();
                  var newLi = document.createElement('li');
                  $(newLi).addClass("list-group-item");
                  if (data.data.is_self){
                    $(newLi).addClass("list-group-item-warning dalistright");
                  }
                  else{
                    $(newLi).addClass("list-group-item-info");
                  }
                  $(newLi).html(data.data.message);
                  $(newLi).appendTo(chatArea);
                  scrollChat("#chatarea" + skey);
                  if (data.data.is_self){
                    $("#listelement" + skey).removeClass("new-message");
                  }
                  else{
                    $("#listelement" + skey).addClass("new-message");
                    if (data.data.hasOwnProperty('temp_user_id')){
                      notifyOperator(key, "chat", """ + repr(str(word("anonymous visitor"))) + """ + ' ' + data.data.temp_user_id + ': ' + data.data.message);
                    }
                    else{
                      if (data.data.first_name && data.data.first_name != ''){
                        notifyOperator(key, "chat", data.data.first_name + ' ' + data.data.last_name + ': ' + data.data.message);
                      }
                      else{
                        notifyOperator(key, "chat", data.data.email + ': ' + data.data.message);
                      }
                    }
                  }
                }
            });
            socket.on('sessionupdate', function(data) {
                //console.log("Got session update: " + data.session.chatstatus);
                draw_session(data.key, data.session);
                check_if_empty();
            });
            socket.on('updatemonitor', function(data) {
                //console.log("Got update monitor response");
                //console.log("updatemonitor: chat partners are: " + data.chatPartners);
                daChatPartners = data.chatPartners;
                daNewPhonePartners = Object();
                daTermPhonePartners = Object();
                daPhonePartners = data.phonePartners;
                var newSubscribedRoles = Object();
                for (var key in data.subscribedRoles){
                    if (data.subscribedRoles.hasOwnProperty(key)){
                        newSubscribedRoles[key] = 1;
                    }
                }
                for (var i = 0; i < data.availRoles.length; ++i){
                    var key = data.availRoles[i];
                    var skey = key.replace(/(:|\.|\[|\]|,|=|\/| )/g, '\\\\$1');
                    if ($("#role" + skey).length == 0){
                        var label = document.createElement('label');
                        $(label).addClass('checkbox-inline');
                        var input = document.createElement('input');
                        var text = document.createTextNode(key);
                        $(input).attr('type', 'checkbox');
                        $(input).attr('id', "role" + key);
                        if (key in newSubscribedRoles){
                            $(input).prop('checked', true);
                        }
                        else{
                            $(input).prop('checked', false);
                        }
                        $(input).val(key);
                        $(input).appendTo($(label));
                        $(text).appendTo($(label));
                        $(label).appendTo($("#monitorroles"));
                        $(input).change(function(){
                            var key = $(this).val();
                            //console.log("change to " + key);
                            if ($(this).is(":checked")) {
                                //console.log("it is checked");
                                daSubscribedRoles[key] = 1;
                            }
                            else{
                                //console.log("it is not checked");
                                if (key in daSubscribedRoles){
                                    delete daSubscribedRoles[key];
                                }
                            }
                            update_monitor();
                        });
                    }
                    else{
                        var input = $("#role" + skey).first();
                        if (key in newSubscribedRoles){
                            $(input).prop('checked', true);
                        }
                        else{
                            $(input).prop('checked', false);
                        }
                    }
                }
                daSubscribedRoles = newSubscribedRoles;
                newDaSessions = Object();
                for (var key in data.sessions){
                    if (data.sessions.hasOwnProperty(key)){
                        var user_id = key.replace(/^.*:userid:/, '');
                        if (true || user_id != daUserid){
                            var obj = data.sessions[key];
                            newDaSessions[key] = obj;
                            draw_session(key, obj);
                        }
                    }
                }
                var toDelete = Array();
                var numSessions = 0;
                for (var key in daSessions){
                    if (daSessions.hasOwnProperty(key)){
                        numSessions++;
                        if (!(key in newDaSessions)){
                            toDelete.push(key);
                        }
                    }
                }
                for (var i = 0; i < toDelete.length; ++i){
                    var key = toDelete[i];
                    undraw_session(key);
                }
                if ($("#monitorsessions").find("li").length > 0){
                    $("#emptylist").addClass("invisible");
                }
                else{
                    $("#emptylist").removeClass("invisible");
                }
            });
        }
        if (daAvailableForChat){
            $("#daNotAvailable").addClass("invisible");
            checkNotifications();
        }
        else{
            $("#daAvailable").addClass("invisible");
        }
        $("#daAvailable").click(function(){
            $("#daAvailable").addClass("invisible");
            $("#daNotAvailable").removeClass("invisible");
            daAvailableForChat = false;
            //console.log("daAvailableForChat: " + daAvailableForChat);
            update_monitor();
            playSound('signinout');
        });
        $("#daNotAvailable").click(function(){
            checkNotifications();
            $("#daNotAvailable").addClass("invisible");
            $("#daAvailable").removeClass("invisible");
            daAvailableForChat = true;
            //console.log("daAvailableForChat: " + daAvailableForChat);
            update_monitor();
            playSound('signinout');
        });
        $( window ).unload(function() {
          if (typeof socket !== 'undefined'){
            socket.emit('terminate');
          }
        });
        if (daUsePhone){
          $("#daPhoneInfo").removeClass("invisible");
          $("#daPhoneNumber").val(daPhoneNumber);
          $("#daPhoneNumber").change(checkPhone);
          $("#daPhoneNumber").bind('keypress keydown keyup', function(e){
            if(e.keyCode == 13) { $(this).blur(); e.preventDefault(); }
          });
        }
        $(window).scroll(function(){
            if (!daShowingNotif){
                return true;
            }
            var obj = Array();
            for (var key in daUpdatedSessions){
                if (daUpdatedSessions.hasOwnProperty(key)){
                    obj.push(key);
                }
            }
            var somethingAbove = false;
            var somethingBelow = false;
            var firstElement = -1;
            var lastElement = -1;
            for (var i = 0; i < obj.length; ++i){
                var result = isHidden(obj[i]);
                if (result == 0){
                    delete daUpdatedSessions[obj[i]];
                }
                else if (result < 0){
                    var top = $(obj[i]).offset().top;
                    somethingAbove = true;
                    if (firstElement == -1 || top < firstElement){
                        firstElement = top;
                    }
                }
                else if (result > 0){
                    var top = $(obj[i]).offset().top;
                    somethingBelow = true;
                    if (lastElement == -1 || top > lastElement){
                        lastElement = top;
                    }
                }
            }
            if (($("#chat-message-above").is(":visible")) && !somethingAbove){
                $("#chat-message-above").hide();
            }
            if (($("#chat-message-below").is(":visible")) && !somethingBelow){
                $("#chat-message-below").hide();
            }
            if (!(somethingAbove || somethingBelow)){
                daShowingNotif = false;
            }
            return true;
        });
        $(".chat-notifier").click(function(e){
            //var key = $(this).data('key');
            var direction = 0;
            if ($(this).attr('id') == "chat-message-above"){
                direction = -1;
            }
            else{
                direction = 1;
            }
            var target = -1;
            var targetElement = null;
            for (var key in daUpdatedSessions){
                if (daUpdatedSessions.hasOwnProperty(key)){
                    var top = $(key).offset().top;
                    if (direction == -1){
                        if (target == -1 || top < target){
                            target = top;
                            targetElement = key;
                        }
                    }
                    else{
                        if (target == -1 || top > target){
                            target = top;
                            targetElement = key;
                        }
                    }
                }
            }
            if (target >= 0){
                $("html, body").animate({scrollTop: target - 60}, 500, function(){
                    $(targetElement).find("input").first().focus();
                });
            }
            e.preventDefault();
            return false;
        })
    });
</script>"""
    return render_template('pages/monitor.html', extra_js=Markup(script)), 200

@app.route('/updatepackage', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer'])
def update_package():
    pip.utils.logging._log_state = threading.local()
    pip.utils.logging._log_state.indentation = 0
    form = UpdatePackageForm(request.form, current_user)
    action = request.args.get('action', None)
    target = request.args.get('package', None)
    if action is not None and target is not None:
        package_list, package_auth = get_package_info()
        the_package = None
        for package in package_list:
            if package.package.name == target:
                the_package = package
                break
        if the_package is not None:
            if action == 'uninstall' and the_package.can_uninstall:
                uninstall_package(target)
            elif action == 'update' and the_package.can_update:
                existing_package = Package.query.filter_by(name=target, active=True).first()
                if existing_package is not None:
                    if existing_package.type == 'git' and existing_package.giturl is not None:
                        install_git_package(target, existing_package.giturl)
                    elif existing_package.type == 'pip':
                        install_pip_package(existing_package.name, existing_package.limitation)
    if request.method == 'POST' and form.validate_on_submit():
        if 'zipfile' in request.files and request.files['zipfile'].filename:
            try:
                the_file = request.files['zipfile']
                filename = secure_filename(the_file.filename)
                pkgname = re.sub(r'\.zip$', r'', filename)
                pkgname = re.sub(r'docassemble-', 'docassemble.', pkgname)
                if user_can_edit_package(pkgname=pkgname):
                    file_number = get_new_file_number(session.get('uid', None), filename)
                    saved_file = SavedFile(file_number, extension='zip', fix=True)
                    zippath = saved_file.path
                    the_file.save(zippath)
                    saved_file.save()
                    saved_file.finalize()
                    #zippath += '.zip'
                    #commands = ['install', zippath, '--egg', '--no-index', '--src=' + tempfile.mkdtemp(), '--log-file=' + pip_log.name, '--upgrade', "--install-option=--user"]
                    install_zip_package(pkgname, file_number)
                else:
                    flash(word("You do not have permission to install this package."), 'error')
            except Exception as errMess:
                flash("Error of type " + str(type(errMess)) + " processing upload: " + str(errMess), "error")
        else:
            if form.giturl.data:
                giturl = form.giturl.data.strip()
                packagename = re.sub(r'.*/', '', giturl)
                if user_can_edit_package(giturl=giturl) and user_can_edit_package(pkgname=packagename):
                    #commands = ['install', '--egg', '--src=' + temp_directory, '--log-file=' + pip_log.name, '--upgrade', "--install-option=--user", 'git+' + giturl + '.git#egg=' + packagename]
                    install_git_package(packagename, giturl)
                else:
                    flash(word("You do not have permission to install this package."), 'error')
            elif form.pippackage.data:
                m =re.match(r'([^>=<]+)([>=<]+.+)', form.pippackage.data)
                if m:
                    packagename = m.group(1)
                    limitation = m.group(2)
                else:
                    packagename = form.pippackage.data
                    limitation = None
                packagename = re.sub(r'[^A-Za-z0-9\_]', '', packagename)
                if user_can_edit_package(pkgname=packagename):
                    install_pip_package(packagename, limitation)
                else:
                    flash(word("You do not have permission to install this package."), 'error')
            else:
                flash(word('You need to either supply a Git URL or upload a file.'), 'error')
    package_list, package_auth = get_package_info()
    form.pippackage.data = None
    form.giturl.data = None
    return render_template('pages/update_package.html', form=form, package_list=package_list), 200

def uninstall_package(packagename):
    logmessage("uninstall_package: " + packagename)
    existing_package = Package.query.filter_by(name=packagename, active=True).first()
    if existing_package is None:
        flash(word("Package did not exist"), 'error')
        return
    the_upload_number = existing_package.upload
    the_package_type = existing_package.type
    for package in Package.query.filter_by(name=packagename, active=True).all():
        package.active = False
    db.session.commit()
    ok, logmessages = docassemble.webapp.update.check_for_updates()
    if ok:
        if the_package_type == 'zip' and the_upload_number is not None:
            SavedFile(the_upload_number).delete()
        trigger_update(except_for=hostname)
        restart_this()
        flash(word("Uninstall successful"), 'success')
    else:
        flash(word("Uninstall not successful"), 'error')
    flash('pip log:  ' + str(logmessages), 'info')
    logmessage(logmessages)
    logmessage("uninstall_package: done")
    return

def install_zip_package(packagename, file_number):
    logmessage("install_zip_package: " + packagename + " " + str(file_number))
    existing_package = Package.query.filter_by(name=packagename, active=True).first()
    if existing_package is None:
        package_auth = PackageAuth(user_id=current_user.id)
        package_entry = Package(name=packagename, package_auth=package_auth, upload=file_number, active=True, type='zip', version=1)
        db.session.add(package_auth)
        db.session.add(package_entry)
    else:
        if existing_package.type == 'zip' and existing_package.upload is not None and existing_package.upload != file_number:
            SavedFile(existing_package.upload).delete()
        existing_package.upload = file_number
        existing_package.active = True
        existing_package.limitation = None
        existing_package.type = 'zip'
        existing_package.version += 1
    db.session.commit()
    #logmessage("Going into check for updates now")
    ok, logmessages = docassemble.webapp.update.check_for_updates()
    #logmessage("Returned from check for updates")
    #logmessage('pip log: ' + str(logmessages), 'info')
    if ok:
        trigger_update(except_for=hostname)
        restart_this()
        flash(word("Install successful"), 'success')
    else:
        flash(word("Install not successful"), 'error')
    flash('pip log: ' + str(logmessages), 'info')
    # pip_log = tempfile.NamedTemporaryFile()
    # commands = ['install', '--quiet', '--egg', '--no-index', '--src=' + tempfile.mkdtemp(), '--upgrade', '--log-file=' + pip_log.name, zippath]
    # returnval = pip.main(commands)
    # if returnval > 0:
    #     with open(pip_log.name) as x:
    #         logfilecontents = x.read()
    #         flash("pip " + " ".join(commands) + "<pre>" + str(logfilecontents) + '</pre>', 'error')
    return

def install_git_package(packagename, giturl):
    logmessage("install_git_package: " + packagename + " " + str(giturl))
    if Package.query.filter_by(name=packagename, active=True).first() is None and Package.query.filter_by(giturl=giturl, active=True).first() is None:
        package_auth = PackageAuth(user_id=current_user.id)
        package_entry = Package(name=packagename, giturl=giturl, package_auth=package_auth, version=1, active=True, type='git')
        db.session.add(package_auth)
        db.session.add(package_entry)
        db.session.commit()
    else:
        package_entry = Package.query.filter_by(name=packagename).first()
        if package_entry is not None:
            if package_entry.type == 'zip' and package_entry.upload is not None:
                SavedFile(package_entry.upload).delete()
            package_entry.version += 1
            package_entry.giturl = giturl
            package_entry.upload = None
            package_entry.limitation = None
            package_entry.type = 'git'
            db.session.commit()
    ok, logmessages = docassemble.webapp.update.check_for_updates()
    if ok:
        trigger_update(except_for=hostname)
        restart_this()
        flash(word("Install successful"), 'success')
    else:
        flash(word("Install not successful"), 'error')
    flash('pip log: ' + str(logmessages), 'info')
    # pip_log = tempfile.NamedTemporaryFile()
    # commands = ['install', '--quiet', '--egg', '--src=' + tempfile.mkdtemp(), '--upgrade', '--log-file=' + pip_log.name, 'git+' + giturl + '.git#egg=' + packagename]
    # returnval = pip.main(commands)
    # if returnval > 0:
    #     with open(pip_log.name) as x: logfilecontents = x.read()
    #     flash("pip " + " ".join(commands) + "<pre>" + str(logfilecontents) + "</pre>", 'error')
    return

def install_pip_package(packagename, limitation):
    existing_package = Package.query.filter_by(name=packagename, active=True).first()
    if existing_package is None:
        package_auth = PackageAuth(user_id=current_user.id)
        package_entry = Package(name=packagename, package_auth=package_auth, limitation=limitation, type='pip')
        db.session.add(package_auth)
        db.session.add(package_entry)
        db.session.commit()
    else:
        if existing_package.type == 'zip' and existing_package.upload is not None:
            SavedFile(existing_package.upload).delete()
        existing_package.version += 1
        existing_package.type = 'pip'
        existing_package.limitation = limitation
        existing_package.giturl = None
        existing_package.upload = None
        db.session.commit()
    ok, logmessages = docassemble.webapp.update.check_for_updates()
    if ok:
        trigger_update(except_for=hostname)
        restart_this()
        flash(word("Install successful"), 'success')
    else:
        flash(word("Install not successful"), 'error')
    flash('pip log: ' + str(logmessages), 'info')
    # pip_log = tempfile.NamedTemporaryFile()
    # commands = ['install', '--quiet', '--egg', '--src=' + tempfile.mkdtemp(), '--upgrade', '--log-file=' + pip_log.name, 'git+' + giturl + '.git#egg=' + packagename]
    # returnval = pip.main(commands)
    # if returnval > 0:
    #     with open(pip_log.name) as x: logfilecontents = x.read()
    #     flash("pip " + " ".join(commands) + "<pre>" + str(logfilecontents) + "</pre>", 'error')
    return

def get_package_info():
    if current_user.has_role('admin'):
        is_admin = True
    else:
        is_admin = False
    package_list = list()
    package_auth = dict()
    for auth in PackageAuth.query.all():
        if auth.package_id not in package_auth:
            package_auth[auth.package_id] = dict()
        package_auth[auth.package_id][auth.user_id] = auth.authtype
    for package in Package.query.filter_by(active=True).order_by(Package.name).all():
        if package.type is not None:
            if package.type == 'zip':
                can_update = False
            else:
                can_update = True
            if is_admin or (package.id in package_auth and current_user.id in package_auth[package.id]):
                can_uninstall = True
            else:
                can_uninstall = False
            if package.core:
                can_uninstall = False
                can_update = is_admin
            package_list.append(Object(package=package, can_update=can_update, can_uninstall=can_uninstall))
    return package_list, package_auth

# @app.route('/testws', methods=['GET', 'POST'])
# def test_websocket():
#     script = '<script type="text/javascript" src="' + url_for('static', filename='app/socket.io.min.js') + '"></script>' + """<script type="text/javascript" charset="utf-8">
#     var socket;
#     $(document).ready(function(){
#         if (location.protocol === 'http:' || document.location.protocol === 'http:'){
#             socket = io.connect("http://" + document.domain + "/interview", {path: '/ws/socket.io'});
#         }
#         if (location.protocol === 'https:' || document.location.protocol === 'https:'){
#             socket = io.connect("https://" + document.domain + "/interview" + location.port, {path: '/wss/socket.io'});
#         }
#         if (typeof socket !== 'undefined') {
#             socket.on('connect', function() {
#                 //console.log("Connected!");
#                 socket.emit('chat_log', {data: 1});
#             });
#             socket.on('mymessage', function(arg) {
#                 //console.log("Received " + arg.data);
#                 $("#daPushResult").html(arg.data);
#             });
#             socket.on('chatmessage', function(arg) {
#                 console.log("Received chat message " + arg.data);
#                 var newDiv = document.createElement('div');
#                 $(newDiv).html(arg.data.message);
#                 $("#daCorrespondence").append(newDiv);
#             });
#         }
#         $("#daSend").click(daSender);
#     });
# </script>"""
#     return render_template('pages/socketserver.html', extra_js=Markup(script)), 200

@app.route('/createplaygroundpackage', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer'])
def create_playground_package():
    form = CreatePlaygroundPackageForm(request.form, current_user)
    current_package = request.args.get('package', None)
    do_install = request.args.get('install', False)
    from_playground = request.args.get('from_playground', False)
    area = dict()
    area['playgroundpackages'] = SavedFile(current_user.id, fix=True, section='playgroundpackages')
    file_list = dict()
    file_list['playgroundpackages'] = sorted([f for f in os.listdir(area['playgroundpackages'].directory) if os.path.isfile(os.path.join(area['playgroundpackages'].directory, f))])
    the_choices = list()
    for file_option in file_list['playgroundpackages']:
        the_choices.append((file_option, file_option))
    form.name.choices = the_choices
    if request.method == 'POST':
        if form.validate():
            current_package = form.name.data
            #flash("form validated", 'success')
        else:
            the_error = ''
            for error in form.name.errors:
                the_error += str(error)
            flash("form did not validate with " + str(form.name.data) + " " + str(the_error) + " among " + str(form.name.choices), 'error')
    if current_package is not None:
        pkgname = re.sub(r'^docassemble-', r'', current_package)
        if not user_can_edit_package(pkgname='docassemble.' + pkgname):
            flash(word('Sorry, that package name is already in use by someone else'), 'error')
            current_package = None
    if current_package is not None and current_package not in file_list['playgroundpackages']:
        flash(word('Sorry, that package name does not exist in the playground'), 'error')
        current_package = None
    if current_package is not None:
        section_sec = {'playgroundtemplate': 'template', 'playgroundstatic': 'static', 'playgroundsources': 'sources', 'playgroundmodules': 'modules'}
        for sec in ['playground', 'playgroundtemplate', 'playgroundstatic', 'playgroundsources', 'playgroundmodules']:
            area[sec] = SavedFile(current_user.id, fix=True, section=sec)
            file_list[sec] = sorted([f for f in os.listdir(area[sec].directory) if os.path.isfile(os.path.join(area[sec].directory, f))])
        if os.path.isfile(os.path.join(area['playgroundpackages'].directory, current_package)):
            filename = os.path.join(area['playgroundpackages'].directory, current_package)
            info = dict()
            with open(filename, 'rU') as fp:
                content = fp.read().decode('utf8')
                info = yaml.load(content)
            for field in ['dependencies', 'interview_files', 'template_files', 'module_files', 'static_files', 'sources_files']:
                if field not in info:
                    info[field] = list()
            for package in ['docassemble', 'docassemble.base']:
                if package not in info['dependencies']:
                    info['dependencies'].append(package)
            author_info = dict()
            author_info['author name and email'] = name_of_user(current_user, include_email=True)
            author_info['author name'] = name_of_user(current_user)
            author_info['author email'] = current_user.email
            author_info['first name'] = current_user.first_name
            author_info['last name'] = current_user.last_name
            author_info['id'] = current_user.id
            nice_name = 'docassemble-' + str(pkgname) + '.zip'
            file_number = get_new_file_number(session.get('uid', None), nice_name)
            saved_file = SavedFile(file_number, extension='zip', fix=True)
            zip_file = docassemble.webapp.files.make_package_zip(pkgname, info, author_info)
            saved_file.copy_from(zip_file.name)
            saved_file.finalize()
            existing_package = Package.query.filter_by(name='docassemble.' + pkgname, active=True).first()
            if existing_package is None:
                package_auth = PackageAuth(user_id=current_user.id)
                package_entry = Package(name='docassemble.' + pkgname, package_auth=package_auth, upload=file_number, type='zip')
                db.session.add(package_auth)
                db.session.add(package_entry)
                #sys.stderr.write("Ok, did the commit\n")
            else:
                existing_package.upload = file_number
                existing_package.active = True
                existing_package.version += 1
            db.session.commit()
            if do_install:
                install_zip_package('docassemble.' + pkgname, file_number)
                return redirect(url_for('playground_packages', file=current_package))
            else:
                response = send_file(saved_file.path, mimetype='application/zip', as_attachment=True, attachment_filename=nice_name)
                response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
                return(response)
    return render_template('pages/create_playground_package.html', form=form, current_package=current_package, package_names=file_list['playgroundpackages']), 200

@app.route('/createpackage', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer'])
def create_package():
    form = CreatePackageForm(request.form, current_user)
    if request.method == 'POST' and form.validate():
        pkgname = re.sub(r'^docassemble-', r'', form.name.data)
        if not user_can_edit_package(pkgname='docassemble.' + pkgname):
            flash(word('Sorry, that package name is already in use by someone else'), 'error')
        else:
            #foobar = Package.query.filter_by(name='docassemble_' + pkgname).first()
            #sys.stderr.write("this is it: " + str(foobar) + "\n")
            initpy = """\
try:
    __import__('pkg_resources').declare_namespace(__name__)
except ImportError:
    __path__ = __import__('pkgutil').extend_path(__path__, __name__)

"""
            licensetext = """\
The MIT License (MIT)

"""
            licensetext += 'Copyright (c) ' + str(datetime.datetime.now().year) + ' ' + unicode(current_user.first_name) + " " + unicode(current_user.last_name) + """

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
            readme = '# docassemble.' + str(pkgname) + "\n\nA docassemble extension.\n\n## Author\n\n" + name_of_user(current_user, include_email=True) + "\n"
            setuppy = """\
#!/usr/bin/env python

import os
import sys
from setuptools import setup, find_packages
from fnmatch import fnmatchcase
from distutils.util import convert_path

standard_exclude = ('*.py', '*.pyc', '*~', '.*', '*.bak', '*.swp*')
standard_exclude_directories = ('.*', 'CVS', '_darcs', './build', './dist', 'EGG-INFO', '*.egg-info')
def find_package_data(where='.', package='', exclude=standard_exclude, exclude_directories=standard_exclude_directories):
    out = {}
    stack = [(convert_path(where), '', package)]
    while stack:
        where, prefix, package = stack.pop(0)
        for name in os.listdir(where):
            fn = os.path.join(where, name)
            if os.path.isdir(fn):
                bad_name = False
                for pattern in exclude_directories:
                    if (fnmatchcase(name, pattern)
                        or fn.lower() == pattern.lower()):
                        bad_name = True
                        break
                if bad_name:
                    continue
                if os.path.isfile(os.path.join(fn, '__init__.py')):
                    if not package:
                        new_package = name
                    else:
                        new_package = package + '.' + name
                        stack.append((fn, '', new_package))
                else:
                    stack.append((fn, prefix + name + '/', package))
            else:
                bad_name = False
                for pattern in exclude:
                    if (fnmatchcase(name, pattern)
                        or fn.lower() == pattern.lower()):
                        bad_name = True
                        break
                if bad_name:
                    continue
                out.setdefault(package, []).append(prefix+name)
    return out

"""
            setuppy += "setup(name='docassemble." + str(pkgname) + "',\n" + """\
      version='0.1',
      description=('A docassemble extension.'),
      author=""" + repr(str(name_of_user(current_user))) + """,
      author_email=""" + repr(str(current_user.email)) + """,
      license='MIT',
      url='http://docassemble.org',
      packages=find_packages(),
      namespace_packages = ['docassemble'],
      zip_safe = False,
      package_data=find_package_data(where='docassemble/""" + str(pkgname) + """/', package='docassemble.""" + str(pkgname) + """'),
     )

"""
            questionfiletext = """\
---
metadata:
  description: |
    Insert description of question file here.
  authors:
    - name: """ + unicode(current_user.first_name) + " " + unicode(current_user.last_name) + """
      organization: """ + unicode(current_user.organization) + """
  revision_date: """ + formatted_current_date() + """
---
mandatory: true
code: |
  user_done
---
question: |
  % if user_doing_well:
  Good to hear it!
  % else:
  Sorry to hear that!
  % endif
sets: user_done
buttons:
  - Exit: exit
  - Restart: restart
---
question: Are you doing well today?
yesno: user_doing_well
...
"""
            templatereadme = """\
# Template directory

If you want to use non-standard document templates with pandoc,
put template files in this directory.
"""
            staticreadme = """\
# Static file directory

If you want to make files available in the web app, put them in
this directory.
"""
            sourcesreadme = """\
# Sources directory

This directory is used to store word translation files, 
machine learning training files, and other source files.
"""
            objectfile = """\
# This is a Python module in which you can write your own Python code,
# if you want to.
#
# Include this module in a docassemble interview by writing:
# ---
# modules:
#   - docassemble.""" + pkgname + """.objects
# ---
#
# Then you can do things like:
# ---
# objects:
#   - favorite_fruit: Fruit
# ---
# mandatory: true
# question: |
#   When I eat some ${ favorite_fruit.name }, 
#   I think, "${ favorite_fruit.eat() }"
# ---
# question: What is the best fruit?
# fields:
#   - Fruit Name: favorite_fruit.name
# ---
from docassemble.base.core import DAObject

class Fruit(DAObject):
    def eat(self):
        return "Yum, that " + self.name + " was good!"
"""
            directory = tempfile.mkdtemp()
            packagedir = os.path.join(directory, 'docassemble-' + str(pkgname))
            questionsdir = os.path.join(packagedir, 'docassemble', str(pkgname), 'data', 'questions')
            templatesdir = os.path.join(packagedir, 'docassemble', str(pkgname), 'data', 'templates')
            staticdir = os.path.join(packagedir, 'docassemble', str(pkgname), 'data', 'static')
            sourcesdir = os.path.join(packagedir, 'docassemble', str(pkgname), 'data', 'sources')
            os.makedirs(questionsdir)
            os.makedirs(templatesdir)
            os.makedirs(staticdir)
            os.makedirs(sourcesdir)
            with open(os.path.join(packagedir, 'README.md'), 'a') as the_file:
                the_file.write(readme)
            with open(os.path.join(packagedir, 'LICENSE'), 'a') as the_file:
                the_file.write(licensetext)
            with open(os.path.join(packagedir, 'setup.py'), 'a') as the_file:
                the_file.write(setuppy)
            with open(os.path.join(packagedir, 'docassemble', '__init__.py'), 'a') as the_file:
                the_file.write(initpy)
            with open(os.path.join(packagedir, 'docassemble', pkgname, '__init__.py'), 'a') as the_file:
                the_file.write('')
            with open(os.path.join(packagedir, 'docassemble', pkgname, 'objects.py'), 'a') as the_file:
                the_file.write(objectfile)
            with open(os.path.join(templatesdir, 'README.md'), 'a') as the_file:
                the_file.write(templatereadme)
            with open(os.path.join(staticdir, 'README.md'), 'a') as the_file:
                the_file.write(staticreadme)
            with open(os.path.join(sourcesdir, 'README.md'), 'a') as the_file:
                the_file.write(sourcesreadme)
            with open(os.path.join(questionsdir, 'questions.yml'), 'a') as the_file:
                the_file.write(questionfiletext)
            nice_name = 'docassemble-' + str(pkgname) + '.zip'
            file_number = get_new_file_number(session.get('uid', None), nice_name)
            saved_file = SavedFile(file_number, extension='zip', fix=True)
            #archive = tempfile.NamedTemporaryFile(delete=False)
            zf = zipfile.ZipFile(saved_file.path, mode='w')
            trimlength = len(directory) + 1
            for root, dirs, files in os.walk(packagedir):
                for file in files:
                    thefilename = os.path.join(root, file)
                    zf.write(thefilename, thefilename[trimlength:])
            zf.close()
            saved_file.save()
            saved_file.finalize()
            existing_package = Package.query.filter_by(name='docassemble.' + pkgname, active=True).first()
            if existing_package is None:
                package_auth = PackageAuth(user_id=current_user.id)
                package_entry = Package(name='docassemble.' + pkgname, package_auth=package_auth, upload=file_number, type='zip')
                db.session.add(package_auth)
                db.session.add(package_entry)
                #sys.stderr.write("Ok, did the commit\n")
            else:
                existing_package.upload = file_number
                existing_package.active = True
                existing_package.version += 1
            db.session.commit()
            response = send_file(saved_file.path, mimetype='application/zip', as_attachment=True, attachment_filename=nice_name)
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
            return response
    return render_template('pages/create_package.html', form=form), 200

def name_of_user(user, include_email=False):
    output = ''
    if user.first_name:
        output += ''
        if user.last_name:
            output += ' '
    if user.last_name:
        output += user.last_name
    if include_email and user.email:
        if output:
            output += ', '
        output += user.email
    return output

@app.route('/restart', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer'])
def restart_page():
    script = """<script>
      function daRestartCallback(data){
        //console.log("Restart result: " + data.success);
      }
      function daRestart(){
        $.ajax({
          type: 'POST',
          url: """ + repr(str(url_for('restart_ajax'))) + """,
          data: 'action=restart',
          success: daRestartCallback,
          dataType: 'json'
        });
        return true;
      }
      $( document ).ready(function() {
        //console.log("restarting");
        setTimeout(daRestart, 500);
      });
    </script>
"""
    next_url = request.args.get('next', url_for('interview_list'))
    extra_meta = """\n    <meta http-equiv="refresh" content="5;URL='""" + next_url + """'">"""
    return render_template('pages/restart.html', extra_meta=Markup(extra_meta), extra_js=Markup(script))

@app.route('/config', methods=['GET', 'POST'])
@login_required
@roles_required(['admin'])
def config_page():
    form = ConfigForm(request.form, current_user)
    content = None
    ok = True
    if request.method == 'POST':
        if form.submit.data and form.config_content.data:
            try:
                yaml.load(form.config_content.data)
            except Exception as errMess:
                ok = False
                content = form.config_content.data
                errMess = word("Configuration not updated.  There was a syntax error in the configuration YAML.") + '<pre>' + str(errMess) + '</pre>'
                flash(str(errMess), 'error')
                logmessage(str(errMess))
            if ok:
                if S3_ENABLED:
                    key = s3.get_key('config.yml')
                    key.set_contents_from_string(form.config_content.data)
                with open(daconfig['config_file'], 'w') as fp:
                    fp.write(form.config_content.data.encode('utf8'))
                    flash(word('The configuration file was saved.'), 'success')
                #session['restart'] = 1
                return redirect(url_for('restart_page'))
        elif form.cancel.data:
            flash(word('Configuration not updated.'), 'info')
            return redirect(url_for('interview_list'))
        else:
            flash(word('Configuration not updated.  There was an error.'), 'error')
            return redirect(url_for('interview_list'))
    if ok:
        with open(daconfig['config_file'], 'rU') as fp:
            content = fp.read().decode('utf8')
    if content is None:
        abort(404)
    return render_template('pages/config.html', extra_css=Markup('\n    <link href="' + url_for('static', filename='codemirror/lib/codemirror.css') + '" rel="stylesheet">'), extra_js=Markup('\n    <script src="' + url_for('static', filename="codemirror/lib/codemirror.js") + '"></script>\n    <script src="' + url_for('static', filename="codemirror/mode/yaml/yaml.js") + '"></script>\n    <script>\n      daTextArea=document.getElementById("config_content");\n      daTextArea.value = ' + json.dumps(content) + ';\n      var daCodeMirror = CodeMirror.fromTextArea(daTextArea, {mode: "yaml", tabSize: 2, tabindex: 70, autofocus: true, lineNumbers: true});\n      daCodeMirror.setOption("extraKeys", { Tab: function(cm) { var spaces = Array(cm.getOption("indentUnit") + 1).join(" "); cm.replaceSelection(spaces); }});\n    </script>'), form=form), 200

def flash_as_html(message, message_type="info"):
    output = """
        <div class="alert alert-""" + str(message_type) + """"><button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>""" + str(message) + """</div>
"""
    return output

def make_example_html(examples, first_id, example_html, data_dict):
    example_html.append('          <ul class="nav nav-pills nav-stacked example-list example-hidden">\n')
    for example in examples:
        if 'list' in example:
            example_html.append('          <li><a class="example-heading">' + example['title'] + '</a>')
            make_example_html(example['list'], first_id, example_html, data_dict)
            example_html.append('          </li>')
            continue
        #logmessage("Doing example with id " + str(example['id']))
        if len(first_id) == 0:
            first_id.append(example['id'])
        example_html.append('            <li><a class="example-link" data-example="' + example['id'] + '">' + example['title'] + '</a></li>')
        data_dict[example['id']] = example
    example_html.append('          </ul>')

@app.route('/playgroundstatic/<userid>/<filename>', methods=['GET'])
def playground_static(userid, filename):
    filename = re.sub(r'[^A-Za-z0-9\-\_\.]', '', filename)
    area = SavedFile(userid, fix=True, section='playgroundstatic')
    filename = os.path.join(area.directory, filename)
    if os.path.isfile(filename):
        extension, mimetype = get_ext_and_mimetype(filename)
        response = send_file(filename, mimetype=str(mimetype))
        return(response)
    abort(404)

@login_required
@roles_required(['developer', 'admin'])
@app.route('/playgroundsources/<userid>/<filename>', methods=['GET'])
def playground_sources(userid, filename):
    filename = re.sub(r'[^A-Za-z0-9\-\_\.]', '', filename)
    area = SavedFile(userid, fix=True, section='playgroundsources')
    filename = os.path.join(area.directory, filename)
    if os.path.isfile(filename):
        extension, mimetype = get_ext_and_mimetype(filename)
        response = send_file(filename, mimetype=str(mimetype))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        return(response)
    abort(404)

@app.route('/playgroundtemplate/<userid>/<filename>', methods=['GET'])
def playground_template(userid, filename):
    filename = re.sub(r'[^A-Za-z0-9\-\_\.]', '', filename)
    area = SavedFile(userid, fix=True, section='playgroundtemplate')
    filename = os.path.join(area.directory, filename)
    if os.path.isfile(filename):
        extension, mimetype = get_ext_and_mimetype(filename)
        response = send_file(filename, mimetype=str(mimetype))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        return(response)
    abort(404)

@app.route('/playgroundfiles', methods=['GET', 'POST'])
@login_required
@roles_required(['developer', 'admin'])
def playground_files():
    form = PlaygroundFilesForm(request.form, current_user)
    formtwo = PlaygroundFilesEditForm(request.form, current_user)
    section = request.args.get('section', 'template')
    the_file = request.args.get('file', '')
    scroll = False
    if the_file:
        scroll = True
    if request.method == 'GET':
        is_new = request.args.get('new', False)
    else:
        is_new = False
    if is_new:
        scroll = True
        the_file = ''
    if request.method == 'POST':
        if (form.section.data):
            section = form.section.data
        if (formtwo.file_name.data):
            the_file = formtwo.file_name.data
            the_file = re.sub(r'[^A-Za-z0-9\-\_\.]+', '_', the_file)
    if section not in ["template", "static", "sources", "modules", "packages"]:
        section = "template"
    area = SavedFile(current_user.id, fix=True, section='playground' + section)
    if request.args.get('delete', False):
        argument = re.sub(r'[^A-Za-z0-9\-\_\.]', '', request.args.get('delete'))
        if argument:
            filename = os.path.join(area.directory, argument)
            if os.path.exists(filename):
                os.remove(filename)
                area.finalize()
                flash(word("Deleted file: ") + argument, "success")
                return redirect(url_for('playground_files', section=section))
            else:
                flash(word("File not found: ") + argument, "error")
    if request.args.get('convert', False):
        argument = re.sub(r'[^A-Za-z0-9\-\_\.]', '', request.args.get('convert'))
        if argument:
            filename = os.path.join(area.directory, argument)
            if os.path.exists(filename):
                to_file = os.path.splitext(argument)[0] + '.md'
                to_path = os.path.join(area.directory, to_file)
                if not os.path.exists(to_path):
                    extension, mimetype = get_ext_and_mimetype(argument)
                    if (mimetype and mimetype in convertible_mimetypes):
                        the_format = convertible_mimetypes[mimetype]
                    elif extension and extension in convertible_extensions:
                        the_format = convertible_extensions[extension]
                    else:
                        flash(word("File format not understood: ") + argument, "error")
                        return redirect(url_for('playground_files', section=section))
                    result = word_to_markdown(filename, the_format)
                    if result is None:
                        flash(word("File could not be converted: ") + argument, "error")
                        return redirect(url_for('playground_files', section=section))
                    shutil.copyfile(result.name, to_path)
                    flash(word("Created new Markdown file called ") + to_file + word("."), "success")
                    area.finalize()
                    return redirect(url_for('playground_files', section=section, file=to_file))
            else:
                flash(word("File not found: ") + argument, "error")
    if request.method == 'POST':
        if 'uploadfile' in request.files and request.files['uploadfile'].filename:
            try:
                up_file = request.files['uploadfile']
                filename = secure_filename(up_file.filename)
                filename = re.sub(r'[^A-Za-z0-9\-\_\.]+', '_', filename)
                filename = os.path.join(area.directory, filename)
                up_file.save(filename)
                area.finalize()
            except Exception as errMess:
                flash("Error of type " + str(type(errMess)) + " processing upload: " + str(errMess), "error")
        if formtwo.delete.data:
            if the_file != '':
                filename = os.path.join(area.directory, the_file)
                if os.path.exists(filename):
                    os.remove(filename)
                    area.finalize()
                    flash(word("Deleted file: ") + the_file, "success")
                    return redirect(url_for('playground_files', section=section))
                else:
                    flash(word("File not found: ") + the_file, "error")            
        if formtwo.submit.data and formtwo.file_content.data:
            if the_file != '':
                if formtwo.original_file_name.data and formtwo.original_file_name.data != the_file:
                    old_filename = os.path.join(area.directory, formtwo.original_file_name.data)
                    if os.path.isfile(old_filename):
                        os.remove(old_filename)
                filename = os.path.join(area.directory, the_file)
                with open(filename, 'w') as fp:
                    fp.write(formtwo.file_content.data.encode('utf8'))
                the_time = formatted_current_time()
                area.finalize()
                flash(str(the_file) + word(' was saved at') + ' ' + the_time + '.', 'success')
                if section == 'modules':
                    #restart_all()
                    return redirect(url_for('restart_page', next=url_for('playground_files', section=section, file=the_file)))
                return redirect(url_for('playground_files', section=section, file=the_file))
            else:
                flash(word('You need to type in a name for the file'), 'error')                
    files = sorted([f for f in os.listdir(area.directory) if os.path.isfile(os.path.join(area.directory, f))])
    editable_files = list()
    convertible_files = list()
    mode = "yaml"
    for a_file in files:
        extension, mimetype = get_ext_and_mimetype(a_file)
        if (mimetype and mimetype in ok_mimetypes) or (extension and extension in ok_extensions):
            editable_files.append(a_file)
    for a_file in files:
        extension, mimetype = get_ext_and_mimetype(a_file)
        b_file = os.path.splitext(a_file)[0] + '.md'
        if b_file not in editable_files and ((mimetype and mimetype in convertible_mimetypes) or (extension and extension in convertible_extensions)):
            convertible_files.append(a_file)
    if request.method == 'GET' and not the_file and not is_new:
        if len(editable_files):
            the_file = editable_files[0]
        else:
            if section == 'modules':
                the_file = 'test.py'
            elif section == 'sources':
                the_file = 'test.json'
            else:
                the_file = 'test.md'
    if the_file != '':
        extension, mimetype = get_ext_and_mimetype(the_file)
        if (mimetype and mimetype in ok_mimetypes):
            mode = ok_mimetypes[mimetype]
        elif (extension and extension in ok_extensions):
            mode = ok_extensions[extension]
    formtwo.original_file_name.data = the_file
    formtwo.file_name.data = the_file
    if the_file != '' and os.path.isfile(os.path.join(area.directory, the_file)):
        filename = os.path.join(area.directory, the_file)
    else:
        filename = None
    if filename is not None:
        area.finalize()
        with open(filename, 'rU') as fp:
            content = fp.read().decode('utf8')
    elif formtwo.file_content.data:
        content = formtwo.file_content.data
    else:
        content = ''
    if (section == "template"):
        header = word("Templates")
        description = 'Add files here that you want want to include in your interviews using "content file," "initial yaml," "additional yaml," "template file," "rtf template file," "pdf template file," or "docx reference file."'
        upload_header = word("Upload a template file")
        edit_header = word('Edit text files')
        after_text = None
    elif (section == "static"):
        header = word("Static files")
        description = 'Add files here that you want to include in your interviews with "images," "image sets," "[FILE]" or "url_of()."'
        upload_header = word("Upload a static file")
        edit_header = word('Edit text files')
        after_text = None
    elif (section == "sources"):
        header = word("Source files")
        description = 'Add files here that you want to make available to your interview code, such as word translation files and training data for machine learning.'
        upload_header = word("Upload a source file")
        edit_header = word('Edit source files')
        after_text = None
    elif (section == "modules"):
        header = word("Modules")
        upload_header = None
        edit_header = None
        description = Markup("""To use this in an interview, write a <code>modules</code> block that refers to this module using Python's syntax for specifying a "relative import" of a module (i.e., prefix the module name with a period).""" + highlight('---\nmodules:\n  - .' + re.sub(r'\.py$', '', the_file) + '\n---', YamlLexer(), HtmlFormatter()))
        after_text = None
    if scroll:
        extra_command = """\
      if ($("#file_name").val().length > 0){
        daCodeMirror.focus();
      }
      else{
        $("#file_name").focus()
      }
      scrollBottom();\n"""
    else:
        extra_command = ""
    return render_template('pages/playgroundfiles.html', extra_css=Markup('\n    <link href="' + url_for('static', filename='codemirror/lib/codemirror.css') + '" rel="stylesheet">\n    <link href="' + url_for('static', filename='app/pygments.css') + '" rel="stylesheet">'), extra_js=Markup('\n    <script src="' + url_for('static', filename="areyousure/jquery.are-you-sure.js") + '"></script>\n    <script src="' + url_for('static', filename="codemirror/lib/codemirror.js") + '"></script>\n    <script src="' + url_for('static', filename="codemirror/mode/" + mode + "/" + mode + ".js") + '"></script>\n    <script>\n      $("#daDelete").click(function(event){if(!confirm("' + word("Are you sure that you want to delete this file?") + '")){event.preventDefault();}});\n      daTextArea = document.getElementById("file_content");\n      var daCodeMirror = CodeMirror.fromTextArea(daTextArea, {mode: "' + mode + '", tabSize: 2, tabindex: 70, autofocus: false, lineNumbers: true});\n      $(window).bind("beforeunload", function(){daCodeMirror.save(); $("#formtwo").trigger("checkform.areYouSure");});\n      $("#formtwo").areYouSure(' + json.dumps({'message': word("There are unsaved changes.  Are you sure you wish to leave this page?")}) + ');\n      $("#formtwo").bind("submit", function(){daCodeMirror.save(); $("#formtwo").trigger("reinitialize.areYouSure"); return true;});\n      daCodeMirror.setOption("extraKeys", { Tab: function(cm) { var spaces = Array(cm.getOption("indentUnit") + 1).join(" "); cm.replaceSelection(spaces); }});\n      function scrollBottom(){$("html, body").animate({ scrollTop: $(document).height() }, "slow");}\n' + extra_command + '    </script>'), header=header, upload_header=upload_header, edit_header=edit_header, description=description, form=form, files=files, section=section, userid=current_user.id, editable_files=editable_files, convertible_files=convertible_files, formtwo=formtwo, current_file=the_file, content=content, after_text=after_text, is_new=str(is_new)), 200

@app.route('/playgroundpackages', methods=['GET', 'POST'])
@login_required
@roles_required(['developer', 'admin'])
def playground_packages():
    form = PlaygroundPackagesForm(request.form, current_user)
    the_file = request.args.get('file', '')
    scroll = False
    package_list, package_auth = get_package_info()
    package_names = sorted([package.package.name for package in package_list])
    for default_package in ['docassemble', 'docassemble.base', 'docassemble.webapp']:
        if default_package in package_names:
            package_names.remove(default_package)
    # if the_file:
    #     scroll = True
    if request.method == 'GET':
        is_new = request.args.get('new', False)
    else:
        is_new = False
    if is_new:
        # scroll = True
        the_file = ''
    area = dict()
    file_list = dict()
    section_name = {'playground': 'Interview files', 'playgroundpackages': 'Packages', 'playgroundtemplate': 'Template files', 'playgroundstatic': 'Static files', 'playgroundsources': 'Source files', 'playgroundmodules': 'Modules'}
    section_sec = {'playgroundtemplate': 'template', 'playgroundstatic': 'static', 'playgroundsources': 'sources', 'playgroundmodules': 'modules'}
    section_field = {'playground': form.interview_files, 'playgroundtemplate': form.template_files, 'playgroundstatic': form.static_files, 'playgroundsources': form.sources_files, 'playgroundmodules': form.module_files}
    for sec in ['playground', 'playgroundpackages', 'playgroundtemplate', 'playgroundstatic', 'playgroundsources', 'playgroundmodules']:
        area[sec] = SavedFile(current_user.id, fix=True, section=sec)
        file_list[sec] = sorted([f for f in os.listdir(area[sec].directory) if os.path.isfile(os.path.join(area[sec].directory, f))])
    for sec, field in section_field.iteritems():
        the_list = []
        for item in file_list[sec]:
            the_list.append((item, item))
        field.choices = the_list
    the_list = []
    for item in package_names:
        the_list.append((item, item))
    form.dependencies.choices = the_list
    validated = False
    if request.method == 'POST' and form.validate():
        the_file = form.file_name.data
        validated = True
    the_file = re.sub(r'[^A-Za-z0-9\-\_\.]+', '-', the_file)
    the_file = re.sub(r'^docassemble-', r'', the_file)
    if not user_can_edit_package(pkgname='docassemble.' + the_file):
        flash(word('Sorry, that package name,') + the_file + word(', is already in use by someone else'), 'error')
        the_file = ''
    if the_file == '' and len(file_list['playgroundpackages']) and not is_new:
        the_file = file_list['playgroundpackages'][0]
    old_info = dict()
    if request.method == 'GET' and the_file != '':
        if the_file != '' and os.path.isfile(os.path.join(area['playgroundpackages'].directory, the_file)):
            filename = os.path.join(area['playgroundpackages'].directory, the_file)
            with open(filename, 'rU') as fp:
                content = fp.read().decode('utf8')
                old_info = yaml.load(content)
                if type(old_info) is dict:
                    for field in ['license', 'description', 'version', 'url', 'readme']:
                        if field in old_info:
                            form[field].data = old_info[field]
                        else:
                            form[field].data = ''
                    for field in ['dependencies', 'interview_files', 'template_files', 'module_files', 'static_files', 'sources_files']:
                        if field in old_info and type(old_info[field]) is list and len(old_info[field]):
                            form[field].data = old_info[field]
        else:
            filename = None
    if request.method == 'POST' and validated:
        if form.delete.data and the_file != '' and os.path.isfile(os.path.join(area['playgroundpackages'].directory, the_file)):
            os.remove(os.path.join(area['playgroundpackages'].directory, the_file))
            area['playgroundpackages'].finalize()
            flash(word("Deleted package"), "success")
            return redirect(url_for('playground_packages'))
        new_info = dict()
        for field in ['license', 'description', 'version', 'url', 'readme', 'dependencies', 'interview_files', 'template_files', 'module_files', 'static_files', 'sources_files']:
            new_info[field] = form[field].data
        #logmessage("found " + str(new_info))
        if form.submit.data or form.download.data or form.install.data:
            if the_file != '':
                area['playgroundpackages'].finalize()
                if form.original_file_name.data and form.original_file_name.data != the_file:
                    old_filename = os.path.join(area['playgroundpackages'].directory, form.original_file_name.data)
                    if os.path.isfile(old_filename):
                        os.remove(old_filename)
                filename = os.path.join(area['playgroundpackages'].directory, the_file)
                with open(filename, 'w') as fp:
                    the_yaml = yaml.safe_dump(new_info, default_flow_style=False, default_style = '|')
                    fp.write(the_yaml.encode('utf8'))
                area['playgroundpackages'].finalize()
                if form.download.data:
                    return redirect(url_for('create_playground_package', package=the_file))
                if form.install.data:
                    return redirect(url_for('create_playground_package', package=the_file, install=True))
                the_time = formatted_current_time()
                flash(word('The package information was saved.'), 'success')
    files = sorted([f for f in os.listdir(area['playgroundpackages'].directory) if os.path.isfile(os.path.join(area['playgroundpackages'].directory, f))])
    editable_files = list()
    mode = "yaml"
    for a_file in files:
        editable_files.append(a_file)
    if request.method == 'GET' and not the_file and not is_new:
        if len(editable_files):
            the_file = editable_files[0]
        else:
            the_file = ''
    form.original_file_name.data = the_file
    form.file_name.data = the_file
    if the_file != '' and os.path.isfile(os.path.join(area['playgroundpackages'].directory, the_file)):
        filename = os.path.join(area['playgroundpackages'].directory, the_file)
    else:
        filename = None
    header = word("Packages")
    upload_header = None
    edit_header = None
    description = Markup("""Describe your package and choose the files from your Playground that will go into it.""")
    after_text = None
    if scroll:
        extra_command = "      scrollBottom();\n"
    else:
        extra_command = ""
    return render_template('pages/playgroundpackages.html', extra_css=Markup('\n    <link href="' + url_for('static', filename='codemirror/lib/codemirror.css') + '" rel="stylesheet">\n    <link href="' + url_for('static', filename='app/pygments.css') + '" rel="stylesheet">'), extra_js=Markup('\n    <script src="' + url_for('static', filename="areyousure/jquery.are-you-sure.js") + '"></script>\n    <script src="' + url_for('static', filename="codemirror/lib/codemirror.js") + '"></script>\n    <script src="' + url_for('static', filename="codemirror/mode/markdown/markdown.js") + '"></script>\n    <script>\n      $("#daDelete").click(function(event){if(!confirm("' + word("Are you sure that you want to delete this package?") + '")){event.preventDefault();}});\n      daTextArea = document.getElementById("readme");\n      var daCodeMirror = CodeMirror.fromTextArea(daTextArea, {mode: "markdown", tabSize: 2, tabindex: 70, autofocus: false, lineNumbers: true});\n      $(window).bind("beforeunload", function(){daCodeMirror.save(); $("#form").trigger("checkform.areYouSure");});\n      $("#form").areYouSure(' + json.dumps({'message': word("There are unsaved changes.  Are you sure you wish to leave this page?")}) + ');\n      $("#form").bind("submit", function(){daCodeMirror.save(); $("#form").trigger("reinitialize.areYouSure"); return true;});\n      daCodeMirror.setOption("extraKeys", { Tab: function(cm) { var spaces = Array(cm.getOption("indentUnit") + 1).join(" "); cm.replaceSelection(spaces); }});\n      function scrollBottom(){$("html, body").animate({ scrollTop: $(document).height() }, "slow");}\n' + extra_command + '    </script>'), header=header, upload_header=upload_header, edit_header=edit_header, description=description, form=form, files=files, file_list=file_list, userid=current_user.id, editable_files=editable_files, current_file=the_file, after_text=after_text, section_name=section_name, section_sec=section_sec, section_field=section_field, package_names=package_names), 200

def public_method(method, the_class):
    if isinstance(method, types.MethodType) and method.__name__ != 'init' and not method.__name__.startswith('_') and method.__name__ in the_class.__dict__:
        return True
    return False

def noquote(string):
    if string is None:
        return string
    string = noquote_match.sub('&quot;', string)
    string = lt_match.sub('&lt;', string)
    string = gt_match.sub('&gt;', string)
    string = amp_match.sub('&amp;', string)
    return string
    # if string is None:
    #     return None
    # newstring = json.dumps(string.replace('\n', ' ').rstrip())
    # return newstring[1:-1]

def infobutton(title):
    docstring = ''
    if 'doc' in title_documentation[title]:
        docstring += noquote(title_documentation[title]['doc']) + "<br>"
    if 'url' in title_documentation[title]:
        docstring += "<a target='_blank' href='" + title_documentation[title]['url'] + "'>" + word("View documentation") + "</a>"
    return '&nbsp;<a class="daquestionsign" role="button" data-container="body" data-toggle="popover" data-placement="auto" data-content="' + docstring + '" title="' + word("Help") + '" data-selector="true" data-title="' + noquote(title_documentation[title].get('title', title)) + '"><i class="glyphicon glyphicon-question-sign"></i></a>'
    
def get_vars_in_use(interview, interview_status, debug_mode=False):
    user_dict = fresh_dictionary()
    has_no_endpoint = False
    if debug_mode:
        has_error = True
        error_message = "Not checking variables because in debug mode."
        error_type = Exception
    else:
        try:
            interview.assemble(user_dict, interview_status)
            has_error = False
        except Exception as errmess:
            has_error = True
            error_message = str(errmess)
            error_type = type(errmess)
            logmessage("Failed assembly with error type " + str(error_type) + " and message: " + error_message)
    fields_used = set()
    names_used = set()
    names_used.update(interview.names_used)
    for question in interview.questions_list:
        names_used.update(question.mako_names)
        names_used.update(question.names_used)
        names_used.update(question.fields_used)
        fields_used.update(question.fields_used)
    for val in interview.questions:
        names_used.add(val)
        fields_used.add(val)
    functions = set()
    modules = set()
    classes = set()
    name_info = copy.deepcopy(base_name_info)
    area = SavedFile(current_user.id, fix=True, section='playgroundtemplate')
    templates = sorted([f for f in os.listdir(area.directory) if os.path.isfile(os.path.join(area.directory, f))])
    area = SavedFile(current_user.id, fix=True, section='playgroundstatic')
    static = sorted([f for f in os.listdir(area.directory) if os.path.isfile(os.path.join(area.directory, f))])
    area = SavedFile(current_user.id, fix=True, section='playgroundsources')
    sources = sorted([f for f in os.listdir(area.directory) if os.path.isfile(os.path.join(area.directory, f))])
    area = SavedFile(current_user.id, fix=True, section='playgroundmodules')
    avail_modules = sorted([re.sub(r'.py$', '', f) for f in os.listdir(area.directory) if os.path.isfile(os.path.join(area.directory, f))])
    for val in user_dict:
        #logmessage("Found val " + str(val) + " of type " + str(type(user_dict[val])))
        if type(user_dict[val]) is types.FunctionType:
            functions.add(val)
            name_info[val] = {'doc': noquote(inspect.getdoc(user_dict[val])), 'name': str(val), 'insert': str(val) + '()', 'tag': str(val) + str(inspect.formatargspec(*inspect.getargspec(user_dict[val])))}
        elif type(user_dict[val]) is types.ModuleType:
            modules.add(val)
            name_info[val] = {'doc': noquote(inspect.getdoc(user_dict[val])), 'name': str(val), 'insert': str(val)}
        # elif type(user_dict[val]) is types.ClassType:
        #     classes.add(val)
        #     name_info[val] = {'doc': noquote(inspect.getdoc(user_dict[val])), 'name': str(val), 'insert': str(val)}
        elif type(user_dict[val]) is types.TypeType or type(user_dict[val]) is types.ClassType:
            classes.add(val)
            bases = list()
            for x in list(user_dict[val].__bases__):
                if x.__name__ != 'DAObject':
                    bases.append(x.__name__)
            methods = inspect.getmembers(user_dict[val], predicate=lambda x: public_method(x, user_dict[val]))
            method_list = list()
            for name, value in methods:
                method_list.append({'insert': '.' + str(name) + '()', 'name': str(name), 'doc': noquote(inspect.getdoc(value)), 'tag': '.' + str(name) + str(inspect.formatargspec(*inspect.getargspec(value)))})
            #logmessage("Defining name_info for " + str(val))
            name_info[val] = {'doc': noquote(inspect.getdoc(user_dict[val])), 'name': str(val), 'insert': str(val), 'bases': bases, 'methods': method_list}
    for val in docassemble.base.functions.pickleable_objects(user_dict):
        names_used.add(val)
        if val not in name_info:
            name_info[val] = dict()
        #name_info[val]['type'] = type(user_dict[val]).__name__
        name_info[val]['type'] = user_dict[val].__class__.__name__
    for var in base_name_info:
        if base_name_info[var]['show']:
            names_used.add(var)
    names_used = set([i for i in names_used if not extraneous_var.search(i)])
    for var in ['_internal']:
        names_used.discard(var)
    view_doc_text = word("View documentation")
    word_documentation = word("Documentation")
    for var in documentation_dict:
        if var not in name_info:
            name_info[var] = dict()
        if 'doc' in name_info[var] and name_info[var]['doc'] is not None:
            name_info[var]['doc'] += '<br>'
        else:
            name_info[var]['doc'] = ''
        name_info[var]['doc'] += "<a target='_blank' href='" + documentation_dict[var] + "'>" + view_doc_text + "</a>"
    for var in name_info:
        if 'methods' in name_info[var]:
            for method in name_info[var]['methods']:
                if var + '.' + method['name'] in documentation_dict:
                    if method['doc'] is None:
                        method['doc'] = ''
                    else:
                        method['doc'] += '<br>'
                    method['doc'] += "<a target='_blank' href='" + documentation_dict[var + '.' + method['name']] + "'>" + view_doc_text + "</a>"                
    content = ''
    if has_error:
        error_style = 'danger'
        if error_type is DAErrorNoEndpoint:
            error_style = 'warning'
            message_to_use = title_documentation['incomplete']['doc']
        elif error_type is DAErrorMissingVariable:
            message_to_use = error_message
        else:
            message_to_use = title_documentation['generic error']['doc']
        content += '\n                  <tr><td class="playground-warning-box"><div class="alert alert-' + error_style + '">' + message_to_use + '</div></td></tr>'
    # content += '\n                  <tr><td><h4>From</h4></td></tr>'
    # content += '\n                  <tr><td><select>'
    # for the_file in files:
    #     content += '<option '
    #     if the_file == current_file:
    #         content += "selected "
    #     content += 'value="' + the_file + '">' + str(the_file) + '</option>'
    # content += '</select></td></tr>'
    names_used = names_used.difference( functions | classes | modules | set(avail_modules) )
    undefined_names = names_used.difference(fields_used | set(base_name_info.keys()) )
    for var in ['_internal']:
        undefined_names.discard(var)
    names_used = names_used.difference( undefined_names )
    if len(undefined_names):
        content += '\n                  <tr><td><h4>Undefined names' + infobutton('undefined') + '</h4></td></tr>'
        for var in sorted(undefined_names):
            content += '\n                  <tr><td><a data-name="' + noquote(var) + '" data-insert="' + noquote(var) + '" class="label label-danger playground-variable">' + var + '</a></td></tr>'
    if len(names_used):
        content += '\n                  <tr><td><h4>Variables' + infobutton('variables') + '</h4></td></tr>'
        for var in sorted(names_used):
            content += '\n                  <tr><td><a data-name="' + noquote(var) + '" data-insert="' + noquote(var) + '" class="label label-primary playground-variable">' + var + '</a>'
            if var in name_info and 'type' in name_info[var] and name_info[var]['type']:
                content +='&nbsp;<span data-ref="' + noquote(name_info[var]['type']) + '" class="daparenthetical">(' + name_info[var]['type'] + ')</span>'
            if var in name_info and 'doc' in name_info[var] and name_info[var]['doc']:
                content += '&nbsp;<a class="dainfosign" role="button" data-container="body" data-toggle="popover" data-placement="auto" data-content="' + name_info[var]['doc'] + '" title="' + word_documentation + '" data-selector="true" data-title="' + var + '"><i class="glyphicon glyphicon-info-sign"></i></a>'
            content += '</td></tr>'
    if len(functions):
        content += '\n                  <tr><td><h4>Functions' + infobutton('functions') + '</h4></td></tr>'
        for var in sorted(functions):
            content += '\n                  <tr><td><a data-name="' + noquote(var) + '" data-insert="' + noquote(name_info[var]['insert']) + '" class="label label-warning playground-variable">' + name_info[var]['tag'] + '</a>'
            if var in name_info and 'doc' in name_info[var] and name_info[var]['doc']:
                content += '&nbsp;<a class="dainfosign" role="button" data-container="body" data-toggle="popover" data-placement="auto" data-content="' + name_info[var]['doc'] + '" title="' + word_documentation + '" data-selector="true" data-title="' + var + '"><i class="glyphicon glyphicon-info-sign"></i></a>'
            content += '</td></tr>'
    if len(classes):
        content += '\n                  <tr><td><h4>Classes' + infobutton('classes') + '</h4></td></tr>'
        for var in sorted(classes):
            content += '\n                  <tr><td><a data-name="' + noquote(var) + '" data-insert="' + noquote(name_info[var]['insert']) + '" class="label label-info playground-variable">' + name_info[var]['name'] + '</a>'
            if name_info[var]['bases']:
                content += '&nbsp;<span data-ref="' + noquote(name_info[var]['bases'][0]) + '" class="daparenthetical">(' + name_info[var]['bases'][0] + ')</span>'
            if name_info[var]['doc']:
                content += '&nbsp;<a class="dainfosign" role="button" data-container="body" data-toggle="popover" data-placement="auto" data-content="' + name_info[var]['doc'] + '" title="' + word_documentation + '" data-selector="true" data-title="' + var + '"><i class="glyphicon glyphicon-info-sign"></i></a>'
            if len(name_info[var]['methods']):
                content += '&nbsp;<a class="dashowmethods" role="button" data-showhide="XMETHODX' + var + '" title="' + word('Methods') + '"><i class="glyphicon glyphicon-cog"></i></a>'
                content += '<table class="invisible" id="XMETHODX' + var + '"><tbody>'
                for method_info in name_info[var]['methods']:
                    content += '<tr><td><a data-name="' + noquote(method_info['name']) + '" data-insert="' + noquote(method_info['insert']) + '" class="label label-warning playground-variable">' + method_info['tag'] + '</a>'
                    if method_info['doc']:
                        content += '&nbsp;<a class="dainfosign" role="button" data-container="body" data-toggle="popover" data-placement="auto" data-content="' + method_info['doc'] + '" title="' + word_documentation + '" data-selector="true" data-title="' + noquote(method_info['name']) + '"><i class="glyphicon glyphicon-info-sign"></i></a>'
                    content += '</td></tr>'
                content += '</tbody></table>'
            content += '</td></tr>'
    if len(modules):
        content += '\n                  <tr><td><h4>Modules defined' + infobutton('modules') + '</h4></td></tr>'
        for var in sorted(modules):
            content += '\n                  <tr><td><a data-name="' + noquote(var) + '" data-insert="' + noquote(name_info[var]['insert']) + '" class="label label-success playground-variable">' + name_info[var]['name'] + '</a>'
            if name_info[var]['doc']:
                content += '&nbsp;<a class="dainfosign" role="button" data-container="body" data-toggle="popover" data-placement="auto" data-content="' + name_info[var]['doc'] + '" title="' + word_documentation + '" data-selector="true" data-title="' + noquote(var) + '"><i class="glyphicon glyphicon-info-sign"></i></a>'
            content += '</td></tr>'
    if len(avail_modules):
        content += '\n                  <tr><td><h4>Modules available in Playground' + infobutton('playground_modules') + '</h4></td></tr>'
        for var in avail_modules:
            content += '\n                  <tr><td><a data-name="' + noquote(var) + '" data-insert=".' + noquote(var) + '" class="label label-success playground-variable">.' + noquote(var) + '</a>'
            content += '</td></tr>'
    if len(templates):
        content += '\n                  <tr><td><h4>Templates' + infobutton('templates') + '</h4></td></tr>'
        for var in templates:
            content += '\n                  <tr><td><a data-name="' + noquote(var) + '" data-insert="' + noquote(var) + '" class="label label-default playground-variable">' + noquote(var) + '</a>'
            content += '</td></tr>'
    if len(static):
        content += '\n                  <tr><td><h4>Static files' + infobutton('static') + '</h4></td></tr>'
        for var in static:
            content += '\n                  <tr><td><a data-name="' + noquote(var) + '" data-insert="' + noquote(var) + '" class="label label-default playground-variable">' + noquote(var) + '</a>'
            content += '</td></tr>'
    if len(sources):
        content += '\n                  <tr><td><h4>Source files' + infobutton('sources') + '</h4></td></tr>'
        for var in sources:
            content += '\n                  <tr><td><a data-name="' + noquote(var) + '" data-insert="' + noquote(var) + '" class="label label-default playground-variable">' + noquote(var) + '</a>'
            content += '</td></tr>'
    if len(interview.images):
        content += '\n                  <tr><td><h4>Decorations' + infobutton('decorations') + '</h4></td></tr>'
        for var in sorted(interview.images):
            content += '\n                  <tr><td><img class="daimageicon" src="' + get_url_from_file_reference(interview.images[var].get_reference()) + '">&nbsp;<a data-name="' + noquote(var) + '" data-insert="' + noquote(var) + '" class="label label-primary playground-variable">' + noquote(var) + '</a>'
            content += '</td></tr>'
    return content

@app.route('/playground', methods=['GET', 'POST'])
@login_required
@roles_required(['developer', 'admin'])
def playground_page():
    form = PlaygroundForm(request.form, current_user)
    interview = None
    the_file = request.args.get('file', '')
    if request.method == 'GET':
        is_new = request.args.get('new', False)
        debug_mode = request.args.get('debug', False)
    else:
        debug_mode = False
        is_new = False
    if is_new:
        the_file = ''
    playground = SavedFile(current_user.id, fix=True, section='playground')
    #path = os.path.join(UPLOAD_DIRECTORY, 'playground', str(current_user.id))
    #if not os.path.exists(path):
    #    os.makedirs(path)
    if request.method == 'POST' and (form.submit.data or form.run.data or form.delete.data):
        if (form.playground_name.data):
            the_file = form.playground_name.data
            the_file = re.sub(r'[^A-Za-z0-9\_\-\.]', '', the_file)
            if not re.search(r'\.ya?ml$', the_file):
                the_file = re.sub(r'\..*', '', the_file) + '.yml'
            if the_file != '':
                filename = os.path.join(playground.directory, the_file)
                if not os.path.isfile(filename):
                    with open(filename, 'a'):
                        os.utime(filename, None)
            else:
                flash(word('You need to type in a name for the interview'), 'error')
        else:
            flash(word('You need to type in a name for the interview'), 'error')
    the_file = re.sub(r'[^A-Za-z0-9\_\-\.]', '', the_file)
    files = sorted([f for f in os.listdir(playground.directory) if os.path.isfile(os.path.join(playground.directory, f))])
    content = ''
    is_default = False
    if request.method == 'GET' and not the_file and not is_new:
        if len(files):
            the_file = files[0]
        else:
            the_file = 'test.yml'
            is_default = True
            content = default_playground_yaml
    active_file = the_file
    if 'variablefile' in session:
        if session['variablefile'] in files:
            active_file = session['variablefile']
        else:
            del session['variablefile']
    if the_file != '':
        filename = os.path.join(playground.directory, the_file)
        if not os.path.isfile(filename):
            with open(filename, 'w') as fp:
                fp.write(content.encode('utf8'))
            playground.finalize()
    post_data = request.form.copy()
    if request.method == 'POST' and 'variablefile' in post_data:
        active_file = post_data['variablefile']
        if post_data['variablefile'] in files:
            session['variablefile'] = active_file
            interview_source = docassemble.base.parse.interview_source_from_string('docassemble.playground' + str(current_user.id) + ':' + active_file)
            interview_source.set_testing(True)
        else:
            if active_file == '':
                active_file = 'test.yml'
            content = ''
            if form.playground_content.data:
                content = form.playground_content.data
            interview_source = docassemble.base.parse.InterviewSourceString(content=content, directory=playground.directory, path="docassemble.playground" + str(current_user.id) + ":" + active_file, testing=True)
        interview = interview_source.get_interview()
        interview_status = docassemble.base.parse.InterviewStatus(current_info=current_info(yaml='docassemble.playground' + str(current_user.id) + ':' + active_file, req=request, action=None))
        variables_html = get_vars_in_use(interview, interview_status, debug_mode=debug_mode)
        return jsonify(variables_html=variables_html)
    if request.method == 'POST' and the_file != '' and form.validate():
        if form.delete.data:
            if os.path.isfile(filename):
                os.remove(filename)
                flash(word('File deleted.'), 'info')
                playground.finalize()
                if 'variablefile' in session and session['variablefile'] == the_file:
                    del session['variablefile']
                return redirect(url_for('playground_page'))
            else:
                flash(word('File not deleted.  There was an error.'), 'error')
        if (form.submit.data or form.run.data) and form.playground_content.data:
            if form.original_playground_name.data and form.original_playground_name.data != the_file:
                old_filename = os.path.join(playground.directory, form.original_playground_name.data)
                if os.path.isfile(old_filename):
                    os.remove(old_filename)
                    files = sorted([f for f in os.listdir(playground.directory) if os.path.isfile(os.path.join(playground.directory, f))])
            the_time = formatted_current_time()
            with open(filename, 'w') as fp:
                fp.write(form.playground_content.data.encode('utf8'))
            for a_file in files:
                docassemble.base.interview_cache.clear_cache('docassemble.playground' + str(current_user.id) + ':' + a_file)
                a_filename = os.path.join(playground.directory, a_file)
                if a_filename != filename and os.path.isfile(a_filename):
                    with open(a_filename, 'a'):
                        os.utime(a_filename, None)
            playground.finalize()
            if form.submit.data:
                flash(word('Saved at') + ' ' + the_time + '.', 'success')
            else:
                flash_message = flash_as_html(word('Saved at') + ' ' + the_time + '.  ' + word('Running in other tab.'), message_type='success')
                interview_source = docassemble.base.parse.interview_source_from_string('docassemble.playground' + str(current_user.id) + ':' + the_file)
                interview_source.set_testing(True)
                interview = interview_source.get_interview()
                interview_status = docassemble.base.parse.InterviewStatus(current_info=current_info(yaml='docassemble.playground' + str(current_user.id) + ':' + active_file, req=request, action=None))
                variables_html = get_vars_in_use(interview, interview_status, debug_mode=debug_mode)
                return jsonify(url=url_for('index', i='docassemble.playground' + str(current_user.id) + ':' + the_file), variables_html=variables_html, flash_message=flash_message)
        else:
            flash(word('Playground not saved.  There was an error.'), 'error')
    interview_path = None
    if the_file != '':
        with open(filename, 'rU') as fp:
            form.original_playground_name.data = the_file
            form.playground_name.data = the_file
            content = fp.read().decode('utf8')
            #if not form.playground_content.data:
                #form.playground_content.data = content
    if active_file != '':
        is_fictitious = False
        interview_path = 'docassemble.playground' + str(current_user.id) + ':' + active_file
        if is_default:
            interview_source = docassemble.base.parse.InterviewSourceString(content=content, directory=playground.directory, path="docassemble.playground" + str(current_user.id) + ":" + active_file, testing=True)
        else:
            interview_source = docassemble.base.parse.interview_source_from_string(interview_path)
            interview_source.set_testing(True)
    else:
        is_fictitious = True
        active_file = 'test.yml'
        if form.playground_content.data:
            content = re.sub(r'\r', '', form.playground_content.data)
            interview_source = docassemble.base.parse.InterviewSourceString(content=content, directory=playground.directory, path="docassemble.playground" + str(current_user.id) + ":" + active_file, testing=True)
        else:
            interview_source = docassemble.base.parse.InterviewSourceString(content='', directory=playground.directory, path="docassemble.playground" + str(current_user.id) + ":" + active_file, testing=True)
    interview = interview_source.get_interview()
    interview_status = docassemble.base.parse.InterviewStatus(current_info=current_info(yaml='docassemble.playground' + str(current_user.id) + ':' + active_file, req=request, action=None))
    variables_html = get_vars_in_use(interview, interview_status, debug_mode=debug_mode)
    pulldown_files = list(files)
    if is_fictitious or is_new or is_default:
        new_active_file = word('(New file)')
        if new_active_file not in pulldown_files:
            pulldown_files.insert(0, new_active_file)
        if is_fictitious:
            active_file = new_active_file
    ajax = """
var exampleData;

function activateExample(id){
  var info = exampleData[id];
  $("#example-source").html(info['html']);
  $("#example-source-before").html(info['before_html']);
  $("#example-source-after").html(info['after_html']);
  $("#example-image-link").attr("href", info['interview']);
  $("#example-image").attr("src", info['image']);
  if (info['documentation'] != null){
    $("#example-documentation-link").attr("href", info['documentation']);
    $("#example-documentation-link").removeClass("example-hidden");
  }
  else{
    $("#example-documentation-link").addClass("example-hidden");
  }
  $(".example-list").addClass("example-hidden");
  $(".example-link").removeClass("example-active");
  $(".example-link").parent().removeClass("active");
  $(".example-link").each(function(){
    if ($(this).data("example") == id){
      $(this).addClass("example-active");
      $(this).parent().addClass("active");
      $(this).parents(".example-list").removeClass("example-hidden");
    }
  });
  $("#hide-full-example").addClass("invisible");
  $("#show-full-example").removeClass("invisible");
  $("#example-source-before").addClass("invisible");
  $("#example-source-after").addClass("invisible");
}

interviewBaseUrl = '""" + url_for('index', i='docassemble.playground' + str(current_user.id) + ':.yml') + """';

function updateRunLink(){
  $("#daRunButton").attr("href", interviewBaseUrl.replace('.yml', $("#daVariables").val()));
}

$( document ).ready(function() {
  $("#daVariables").change(function(event){
    daCodeMirror.save();
    updateRunLink();
    $.ajax({
      type: "POST",
      url: """ + '"' + url_for('playground_page') + '"' + """,
      data: $("#form").serialize() + '&variablefile=' + $(this).val(),
      success: function(data){
        //console.log("foobar1")
        $("#daplaygroundtable").html(data.variables_html)
        $(function () {
          $('[data-toggle="popover"]').popover({trigger: 'hover', html: true})
        });
        //console.log("foobar2")
      },
      dataType: 'json'
    });
    $(this).blur();
  });
  $("#daRun").click(function(event){
    daCodeMirror.save();
    $.ajax({
      type: "POST",
      url: """ + '"' + url_for('playground_page') + '"' + """,
      data: $("#form").serialize() + '&run=Save+and+Run',
      success: function(data){
        if ($("#flash").length){
          $("#flash").html(data.flash_message)
        }
        else{
          $("#main").prepend('<div class="topcenter col-centered col-sm-7 col-md-6 col-lg-5" id="flash">' + data.flash_message + '</div>')
        }
        $("#daplaygroundtable").html(data.variables_html)
        window.open(data.url, '_blank');
        $("#form").trigger("reinitialize.areYouSure")
        $(function () {
          $('[data-toggle="popover"]').popover({trigger: 'hover', html: true})
        });
      },
      dataType: 'json'
    });
    event.preventDefault();
  });
  $(".playground-variable").on("click", function(){
    daCodeMirror.replaceSelection($(this).data("insert"), "around");
    daCodeMirror.focus();
  });

  $(".daparenthetical").on("click", function(event){
    var reference = $(this).data("ref");
    //console.log("reference is " + reference)
    var target = $('[data-name="' + reference + '"]').first();
    if (target != null){
      //console.log("scrolltop is now " + $('#daplaygroundpanel').scrollTop());
      //console.log("Scrolling to " + target.position().top);
      $('#daplaygroundpanel').animate({
          scrollTop: target.position().top
      }, 1000);
    }
    event.preventDefault();
  });

  $(".dashowmethods").on("click", function(event){
    var target_id = $(this).data("showhide");
    $("#" + target_id).toggleClass("invisible");
  });

  $(".example-link").on("click", function(){
    var id = $(this).data("example");
    activateExample(id);
  });

  $(".example-copy").on("click", function(){
    if (daCodeMirror.somethingSelected()){
      daCodeMirror.replaceSelection("");
    }
    var id = $(".example-active").data("example");
    var curPos = daCodeMirror.getCursor();
    var notFound = 1;
    var insertLine = daCodeMirror.lastLine();
    daCodeMirror.eachLine(curPos.line, insertLine, function(line){
      if (notFound){
        if (line.text.substring(0, 3) == "---" || line.text.substring(0, 3) == "..."){
          insertLine = daCodeMirror.getLineNumber(line)
          //console.log("Found break at line number " + insertLine)
          notFound = 0;
        }
      }
    });
    if (notFound){
      daCodeMirror.setSelection({'line': insertLine, 'ch': null});
      daCodeMirror.replaceSelection("\\n---\\n" + exampleData[id]['source'] + "\\n", "around");
    }
    else{
      daCodeMirror.setSelection({'line': insertLine, 'ch': 0});
      daCodeMirror.replaceSelection("---\\n" + exampleData[id]['source'] + "\\n", "around");
    }
    daCodeMirror.focus();
  });

  $(".example-heading").on("click", function(){
    var list = $(this).parent().children("ul").first();
    if (list != null){
      if (!list.hasClass("example-hidden")){
        return;
      }
      $(".example-list").addClass("example-hidden");
      var new_link = $(this).parent().find("a.example-link").first();
      if (new_link.length){
        var id = new_link.data("example");
        activateExample(id);  
      }
    }
  });

  $(function () {
    $('[data-toggle="popover"]').popover({trigger: 'hover', html: true})
  });

  $("#show-full-example").on("click", function(){
    var id = $(".example-active").data("example");
    var info = exampleData[id];
    $(this).addClass("invisible");
    $("#hide-full-example").removeClass("invisible");
    $("#example-source-before").removeClass("invisible");
    $("#example-source-after").removeClass("invisible");
  });

  $("#hide-full-example").on("click", function(){
    var id = $(".example-active").data("example");
    var info = exampleData[id];
    $(this).addClass("invisible");
    $("#show-full-example").removeClass("invisible");
    $("#example-source-before").addClass("invisible");
    $("#example-source-after").addClass("invisible");
  });
  if ($("#playground_name").val().length > 0){
    daCodeMirror.focus();
  }
  else{
    $("#playground_name").focus()
  }
  updateRunLink();
});
"""
    example_html = list()
    example_html.append('        <div class="col-md-2">\n          <h4>' + word("Example blocks") +'</h4>')
    first_id = list()
    data_dict = dict()
    make_example_html(get_examples(), first_id, example_html, data_dict)
    example_html.append('        </div>')
    example_html.append('        <div class="col-md-6"><h4>' + word("Preview") + '<a target="_blank" class="label label-primary example-documentation example-hidden" id="example-documentation-link">' + word('View documentation') + '</a></h4><a href="#" target="_blank" id="example-image-link"><img title="' + word('Click to try this interview') + '" class="example_screenshot" id="example-image"></a></div>')
    example_html.append('        <div class="col-md-4 example-source-col"><h4>' + word('Source') + ' <a class="label label-success example-copy">' + word('Insert') + '</a></h4><div id="example-source-before" class="invisible"></div><div id="example-source"></div><div id="example-source-after" class="invisible"></div><div><a class="example-hider" id="show-full-example">' + word("Show context of example") + '</a><a class="example-hider invisible" id="hide-full-example">' + word("Hide context of example") + '</a></div></div>')
    return render_template('pages/playground.html', page_title=word("Playground"), extra_css=Markup('\n    <link href="' + url_for('static', filename='codemirror/lib/codemirror.css') + '" rel="stylesheet">\n    <link href="' + url_for('static', filename='app/pygments.css') + '" rel="stylesheet">'), extra_js=Markup('\n    <script src="' + url_for('static', filename="areyousure/jquery.are-you-sure.js") + '"></script>\n    <script src="' + url_for('static', filename="codemirror/lib/codemirror.js") + '"></script>\n    <script src="' + url_for('static', filename="codemirror/mode/yaml/yaml.js") + '"></script>\n    <script>\n      $("#daDelete").click(function(event){if(!confirm("' + word("Are you sure that you want to delete this playground file?") + '")){event.preventDefault();}});\n      daTextArea = document.getElementById("playground_content");\n      var daCodeMirror = CodeMirror.fromTextArea(daTextArea, {mode: "yaml", tabSize: 2, tabindex: 70, autofocus: false, lineNumbers: true});\n      $(window).bind("beforeunload", function(){daCodeMirror.save(); $("#form").trigger("checkform.areYouSure");});\n      $("#form").areYouSure(' + json.dumps({'message': word("There are unsaved changes.  Are you sure you wish to leave this page?")}) + ');\n      $("#form").bind("submit", function(){daCodeMirror.save(); $("#form").trigger("reinitialize.areYouSure"); return true;});\n      daCodeMirror.setSize(null, "400px");\n      daCodeMirror.setOption("extraKeys", { Tab: function(cm) { var spaces = Array(cm.getOption("indentUnit") + 1).join(" "); cm.replaceSelection(spaces); }});\n' + indent_by(ajax, 6) + '\n      exampleData = ' + str(json.dumps(data_dict)) + ';\n      activateExample("' + str(first_id[0]) + '");\n    </script>'), form=form, files=files, pulldown_files=pulldown_files, current_file=the_file, active_file=active_file, content=content, variables_html=Markup(variables_html), example_html=Markup("\n".join(example_html)), interview_path=interview_path, is_new=str(is_new)), 200

# nameInfo = ' + str(json.dumps(vars_in_use['name_info'])) + ';      

# def mydump(data_dict):
#     output = ""
#     for key, val in data_dict.iteritems():
#         output += "      exampleData[" + str(repr(key)) + "] = " + str(json.dumps(val)) + "\n"
#     return output

@app.route('/packages', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer'])
def package_page():
    return render_template('pages/packages.html'), 200

def make_image_files(path):
    #logmessage("make_image_files on " + str(path))
    if PDFTOPPM_COMMAND is not None:
        args = [PDFTOPPM_COMMAND, '-r', str(PNG_RESOLUTION), '-png', path, path + 'page']
        result = call(args)
        if result > 0:
            raise DAError("Call to pdftoppm failed")
        args = [PDFTOPPM_COMMAND, '-r', str(PNG_SCREEN_RESOLUTION), '-png', path, path + 'screen']
        result = call(args)
        if result > 0:
            raise DAError("Call to pdftoppm failed")
    return

@app.errorhandler(Exception)
def server_error(the_error):
    errmess = unicode(the_error)
    if type(the_error) is DAError:
        the_trace = None
        logmessage(errmess)
    else:
        the_trace = traceback.format_exc()
        logmessage(the_trace)
    flask_logtext = []
    with open(LOGFILE) as the_file:
        for line in the_file:
            if re.match('Exception', line):
                flask_logtext = []
            flask_logtext.append(line)
    # apache_logtext = []
    # with open(APACHE_LOGFILE) as the_file:
    #     for line in the_file:
    #         if re.search('configured -- resuming normal operations', line):
    #             apache_logtext = []
    #         apache_logtext.append(line)
    # errmess = re.sub(r'\n', '<br>', errmess)
    if re.search(r'\n', errmess):
        errmess = '<pre>' + errmess + '</pre>'
    else:
        errmess = '<blockquote>' + errmess + '</blockquote>'
    return render_template('pages/501.html', error=errmess, logtext=str(the_trace)), 501

def trigger_update(except_for=None):
    logmessage("trigger_update: except_for is " + str(except_for))
    if USING_SUPERVISOR:
        for host in Supervisors.query.all():
            if host.url and not (except_for and host.hostname == except_for):
                if host.hostname == hostname:
                    the_url = 'http://localhost:9001'
                else:
                    the_url = host.url
                args = [SUPERVISORCTL, '-s', the_url, 'start update']
                result = call(args)
                if result == 0:
                    logmessage("trigger_update: sent reset to " + str(host.hostname))
                else:
                    logmessage("trigger_update: call to supervisorctl on " + str(host.hostname) + " was not successful")
    return

def restart_on(host):
    if host.hostname == hostname:
        the_url = 'http://localhost:9001'
    else:
        the_url = host.url
    if re.search(r':(web|all):', host.role):
        args = [SUPERVISORCTL, '-s', the_url, 'start reset']
    result = call(args)
    if result == 0:
        logmessage("restart_on: sent reset to " + str(host.hostname))
    else:
        logmessage("restart_on: call to supervisorctl with reset on " + str(host.hostname) + " was not successful")
    # if re.search(r':(celery|all):', host.role):
    #     args = [SUPERVISORCTL, '-s', the_url, 'restart celery']
    # result = call(args)
    # if result == 0:
    #     logmessage("restart_on: sent restart celery to " + str(host.hostname))
    # else:
    #     logmessage("restart_on: call to supervisorctl with restart celery on " + str(host.hostname) + " was not successful")
    return

def restart_all():
    restart_others()
    restart_this()
    return

def restart_this():
    if USING_SUPERVISOR:
        for host in Supervisors.query.all():
            if host.url:
                logmessage("restart_this: considering " + str(host.hostname) + "against " + str(hostname))
                if host.hostname == hostname:
                    restart_on(host)
            else:
                logmessage("restart_this: unable to get host url")
    else:
        logmessage("restart_this: touched wsgi file")
        wsgi_file = WEBAPP_PATH
        if os.path.isfile(wsgi_file):
            with open(wsgi_file, 'a'):
                os.utime(wsgi_file, None)
    return

def restart_others():
    logmessage("Got to restart_others")
    if USING_SUPERVISOR:
        for host in Supervisors.query.all():
            if host.url:
                if host.hostname != hostname:
                    restart_on(host)
            else:
                logmessage("restart_others: unable to get host url")
    return

# @app.route('/testpost', methods=['GET', 'POST'])
# def test_post():
#     errmess = "Hello, " + str(request.method) + "!"
#     is_redir = request.args.get('redir', None)
#     if is_redir or request.method == 'GET':
#         return render_template('pages/testpost.html', error=errmess), 200
#     newargs = dict(request.args)
#     newargs['redir'] = '1'
#     logtext = url_for('test_post', **newargs)
#     #return render_template('pages/testpost.html', error=errmess, logtext=logtext), 200
#     return redirect(logtext, code=307)

@app.route('/packagestatic/<package>/<filename>', methods=['GET'])
def package_static(package, filename):
    the_file = docassemble.base.functions.package_data_filename(str(package) + ':data/static/' + str(filename))
    if the_file is None:
        abort(404)
    extension, mimetype = get_ext_and_mimetype(the_file)
    response = send_file(the_file, mimetype=str(mimetype))
    return(response)

def current_info(yaml=None, req=None, action=None, location=None):
    if current_user.is_authenticated and not current_user.is_anonymous:
        ext = dict(email=current_user.email, roles=[role.name for role in current_user.roles], theid=current_user.id, firstname=current_user.first_name, lastname=current_user.last_name, nickname=current_user.nickname, country=current_user.country, subdivisionfirst=current_user.subdivisionfirst, subdivisionsecond=current_user.subdivisionsecond, subdivisionthird=current_user.subdivisionthird, organization=current_user.organization)
    else:
        ext = dict(email=None, theid=session.get('tempuser', None), roles=list())
    if req is None:
        url = 'http://localhost'
        secret = None
    else:
        url = req.base_url
        secret = req.cookies.get('secret', None)
    return_val = {'session': session.get('uid', None), 'secret': secret, 'yaml_filename': yaml, 'url': url, 'user': {'is_anonymous': current_user.is_anonymous, 'is_authenticated': current_user.is_authenticated}}
    if action is not None:
        return_val.update(action)
    if location is not None:
        ext['location'] = location
    else:
        ext['location'] = None
    return_val['user'].update(ext)
    return(return_val)

def html_escape(text):
    text = re.sub('&', '&amp;', text)
    text = re.sub('<', '&lt;', text)
    text = re.sub('>', '&gt;', text)
    return text;

def indent_by(text, num):
    if not text:
        return ""
    return (" " * num) + re.sub(r'\n', "\n" + (" " * num), text).rstrip() + "\n"

# def indent_by(text, num):
#     return (" " * num) + re.sub(r'\n', "\n" + (" " * num), text).rstrip() + "\n"
    
# @app.route('/twiliotest', methods=['GET', 'POST'])
# def twilio_test():
#     account_sid = "ACfad8e668b5f9e15d499ab823523b9358"
#     auth_token = "86549c9a407b25d32f21c758e7b09546"
#     application_sid = "AP67affb53323193b8e2af0872aad387ad"
#     capability = TwilioCapability(account_sid, auth_token)
#     capability.allow_client_outgoing(application_sid)
#     token = capability.generate()
#     return render_template('pages/twiliotest.html', token=token)

@app.route('/logfile/<filename>', methods=['GET'])
@login_required
@roles_required(['admin', 'developer'])
def logfile(filename):
    if LOGSERVER is None:
        the_file = os.path.join(LOG_DIRECTORY, filename)
        if not os.path.isfile(the_file):
            abort(404)
    else:
        h = httplib2.Http()
        resp, content = h.request("http://" + LOGSERVER + ':8080', "GET")
        the_file, headers = urllib.urlretrieve("http://" + LOGSERVER + ':8080/' + urllib.quote(filename))
    response = send_file(the_file, as_attachment=True, mimetype='text/plain', attachment_filename=filename, cache_timeout=0)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    return(response)

@app.route('/logs', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer'])
def logs():
    form = LogForm(request.form, current_user)
    the_file = request.args.get('file', None)
    default_filter_string = ''
    if request.method == 'POST' and form.file_name.data:
        the_file = form.file_name.data
    if LOGSERVER is None:
        call_sync()
        files = sorted([f for f in os.listdir(LOG_DIRECTORY) if os.path.isfile(os.path.join(LOG_DIRECTORY, f))])
        if the_file is None and len(files):
            if 'docassemble.log' in files:
                the_file = 'docassemble.log'
            else:
                the_file = files[0]
        if the_file is not None:
            filename = os.path.join(LOG_DIRECTORY, the_file)
            # if (not os.path.isfile(filename)) and len(files):
            #     the_file = files[0]
            # else:
            #     the_file = None
    else:
        h = httplib2.Http()
        resp, content = h.request("http://" + LOGSERVER + ':8080', "GET")
        if int(resp['status']) >= 200 and int(resp['status']) < 300:
            files = content.split("\n")
        else:
            abort(404)
        if len(files):
            if the_file is None:
                the_file = files[0]
            filename, headers = urllib.urlretrieve("http://" + LOGSERVER + ':8080/' + urllib.quote(the_file))
    if len(files):
        if request.method == 'POST' and form.submit.data and form.filter_string.data:
            default_filter_string = form.filter_string.data
            reg_exp = re.compile(form.filter_string.data)
            temp_file = tempfile.NamedTemporaryFile()
            with open(filename, 'rU') as fp:
                for line in fp:
                    if reg_exp.search(line):
                        temp_file.write(line)
            lines = tailer.tail(temp_file, 30)
        else:
            lines = tailer.tail(open(filename), 30)
        content = "\n".join(lines)
    else:
        content = "No log files available"
    return render_template('pages/logs.html', form=form, files=files, current_file=the_file, content=content, default_filter_string=default_filter_string), 200

def call_sync():
    if not USING_SUPERVISOR:
        return
    args = [SUPERVISORCTL, '-s', 'http://localhost:9001', 'start', 'sync']
    result = call(args)
    if result == 0:
        logmessage("logs: sent message to " + hostname)
    else:
        logmessage("logs: call to supervisorctl on " + hostname + " was not successful")
        abort(404)
    in_process = 1
    counter = 10
    check_args = [SUPERVISORCTL, '-s', 'http://localhost:9001', 'status', 'sync']
    while in_process == 1 and counter > 0:
        output, err = Popen(check_args, stdout=PIPE, stderr=PIPE).communicate()
        if not re.search(r'RUNNING', output):
            in_process = 0
        else:
            time.sleep(1)
        counter -= 1
    return

@app.route('/reqdev', methods=['GET', 'POST'])
@login_required
def request_developer():
    from docassemble.webapp.users.forms import RequestDeveloperForm
    form = RequestDeveloperForm(request.form, current_user)
    recipients = list()
    if request.method == 'POST':
        for user in User.query.filter_by(active=True).all():
            for role in user.roles:
                if role.name == 'admin':
                    recipients.append(user.email)
        url = request.base_url
        url = re.sub(r'^(https?://[^/]+)/.*', r'\1', url)
        body = "User " + str(current_user.email) + " (" + str(current_user.id) + ") has requested developer privileges.\n\n"
        if form.reason.data:
            body += "Reason given: " + str(form.reason.data) + "\n\n"
        body += "Go to " + str(url) + url_for('edit_user_profile_page', id=current_user.id) + " to change the user's privileges."
        from flask_mail import Message
        msg = Message("Request for developer account from " + str(current_user.email), recipients=recipients, body=body)
        if not len(recipients):
            flash(word('No administrators could be found.'), 'error')
        else:
            try:
                async_mail(msg)
                flash(word('Your request was submitted.'), 'success')
            except:
                flash(word('We were unable to submit your request.'), 'error')
        return redirect(url_for('index'))
    return render_template('users/request_developer.html', form=form)

@app.route('/utilities', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer'])
def utilities():
    form = Utilities(request.form)
    fields_output = None
    if request.method == 'POST':
        if 'pdffile' in request.files and request.files['pdffile'].filename:
            pdf_file = tempfile.NamedTemporaryFile(mode="wb", suffix=".pdf", delete=True)
            the_file = request.files['pdffile']
            the_file.save(pdf_file.name)
            fields = docassemble.base.pdftk.read_fields(pdf_file.name)
            if fields is None:
                fields_output = word("Error: no fields could be found in the file")
            else:
                fields_output = "---\nquestion: " + word("something") + "\nsets: " + word('some_variable') + "\nattachment:" + "\n  - name: " + os.path.splitext(the_file.filename)[0] + "\n    filename: " + os.path.splitext(the_file.filename)[0] + "\n    pdf template file: " + the_file.filename + "\n    fields:\n"
                for field, default, pageno, rect, field_type in fields:
                    fields_output += '      "' + field + '": ' + default + "\n"
                fields_output += "---"
    return render_template('pages/utilities.html', form=form, fields=fields_output)

def formatted_current_time():
    if current_user.timezone:
        the_timezone = pytz.timezone(current_user.timezone)
    else:
        the_timezone = pytz.timezone(get_default_timezone())
    return datetime.datetime.utcnow().replace(tzinfo=tz.tzutc()).astimezone(the_timezone).strftime('%H:%M:%S %Z')

def formatted_current_date():
    if current_user.timezone:
        the_timezone = pytz.timezone(current_user.timezone)
    else:
        the_timezone = pytz.timezone(get_default_timezone())
    return datetime.datetime.utcnow().replace(tzinfo=tz.tzutc()).astimezone(the_timezone).strftime("%Y-%m-%d")

@app.route('/save', methods=['GET', 'POST'])
def save_for_later():
    if current_user.is_authenticated and not current_user.is_anonymous:
        return render_template('pages/save_for_later.html', interview=sdf)
    secret = request.cookies.get('secret', None)

@app.route('/interviews', methods=['GET', 'POST'])
@login_required
def interview_list():
    if current_user.timezone:
        the_timezone = pytz.timezone(current_user.timezone)
    else:
        the_timezone = pytz.timezone(get_default_timezone())
    secret = request.cookies.get('secret', None)
    #logmessage("interview_list: secret is " + str(secret))
    if 'action' in request.args and request.args.get('action') == 'delete':
        yaml_file = request.args.get('filename', None)
        session_id = request.args.get('session', None)
        if yaml_file is not None and session_id is not None:
            manual_checkout()
            obtain_lock(session_id, yaml_file)
            reset_user_dict(session_id, yaml_file)
            release_lock(session_id, yaml_file)
            flash(word("Deleted interview"), 'success')
            return redirect(url_for('interview_list'))
    subq = db.session.query(db.func.max(UserDict.indexno).label('indexno'), UserDict.filename, UserDict.key).group_by(UserDict.filename, UserDict.key).subquery()
    interview_query = db.session.query(UserDictKeys.filename, UserDictKeys.key, UserDict.dictionary, UserDict.encrypted).filter(UserDictKeys.user_id == current_user.id).join(subq, and_(subq.c.filename == UserDictKeys.filename, subq.c.key == UserDictKeys.key)).join(UserDict, and_(UserDict.indexno == subq.c.indexno, UserDict.key == UserDictKeys.key, UserDict.filename == UserDictKeys.filename)).group_by(UserDictKeys.filename, UserDictKeys.key, UserDict.dictionary, UserDict.encrypted)
    #logmessage(str(interview_query))
    interviews = list()
    for interview_info in interview_query:
        try:
            interview = docassemble.base.interview_cache.get_interview(interview_info.filename)
        except:
            logmessage("Unable to load interview file " + interview_info.filename)
            continue
        if len(interview.metadata):
            metadata = interview.metadata[0]
            interview_title = metadata.get('title', metadata.get('short title', word('Untitled'))).rstrip()
        else:
            interview_title = word('Untitled')
        #logmessage("Found old interview with title " + interview_title)
        if interview_info.encrypted:
            try:
                dictionary = decrypt_dictionary(interview_info.dictionary, secret)
            except:
                logmessage("Unable to decrypt dictionary with secret " + str(secret))
                continue
        else:
            dictionary = unpack_dictionary(interview_info.dictionary)
        starttime = nice_date_from_utc(dictionary['_internal']['starttime'], timezone=the_timezone)
        modtime = nice_date_from_utc(dictionary['_internal']['modtime'], timezone=the_timezone)
        interviews.append({'interview_info': interview_info, 'dict': dictionary, 'modtime': modtime, 'starttime': starttime, 'title': interview_title})
    return render_template('pages/interviews.html', interviews=sorted(interviews, key=lambda x: x['dict']['_internal']['starttime']))

# @user_logged_in.connect_via(app)
# def _after_login_hook(sender, user, **extra):
#     if 'i' in session and 'uid' in session:
#         save_user_dict_key(session['uid'], session['i'])
#         session['key_logged'] = True 
#     newsecret = substitute_secret(secret, pad_to_16(MD5.MD5Hash(data=password).hexdigest()))
#     # Redirect to 'next' URL
#     response = redirect(next)
#     response.set_cookie('secret', newsecret)
#     return response

@app.teardown_appcontext
def close_db(error):
    if hasattr(db, 'engine'):
        db.engine.dispose()

@app.route('/webrtc')
def webrtc():
    return render_template('pages/webrtc.html')

alphanumeric_only = re.compile('[\W_]+')
phone_pattern = re.compile(r"^[\d\+\-\(\) ]+$")

@app.route('/webrtc_token', methods=['GET'])
def webrtc_token():
    if twilio_config is None:
        logmessage("Could not get twilio configuration")
        return
    account_sid = twilio_config['name']['default'].get('account sid', None)
    auth_token = twilio_config['name']['default'].get('auth token', None)
    application_sid = twilio_config['name']['default'].get('app sid', None)

    logmessage("account sid is " + str(account_sid) + "; auth_token is " + str(auth_token) + "; application_sid is " + str(application_sid))

    identity = 'testuser2'

    capability = TwilioCapability(account_sid, auth_token)
    capability.allow_client_outgoing(application_sid)
    capability.allow_client_incoming(identity)
    token = capability.generate()

    return jsonify(identity=identity, token=token)

@app.route("/voice", methods=['POST', 'GET'])
def voice():
    resp = twilio.twiml.Response()
    if twilio_config is None:
        logmessage("Ignoring call to voice because Twilio not enabled")
        return Response(str(resp), mimetype='text/xml')
    if "AccountSid" not in request.form or request.form["AccountSid"] != twilio_config['name']['default'].get('account sid', None):
        logmessage("Request to voice did not authenticate")
        return Response(str(resp), mimetype='text/xml')
    for item in request.form:
        logmessage("Item " + str(item) + " is " + str(request.form[item]))
    with resp.gather(action="/digits", finishOnKey='#', method="POST", timeout=10, numDigits=5) as g:
        g.say(word("Please enter the four digit code, followed by the pound sign."))

    # twilio_config = daconfig.get('twilio', None)
    # if twilio_config is None:
    #     logmessage("Could not get twilio configuration")
    #     return
    # twilio_caller_id = twilio_config.get('number', None)
    # if "To" in request.form and request.form["To"] != '':
    #     dial = resp.dial(callerId=twilio_caller_id)
    #     if phone_pattern.match(request.form["To"]):
    #         dial.number(request.form["To"])
    #     else:
    #         dial.client(request.form["To"])
    # else:
    #     resp.say("Thanks for calling!")

    return Response(str(resp), mimetype='text/xml')

@app.route("/digits", methods=['POST', 'GET'])
def digits():
    resp = twilio.twiml.Response()
    if twilio_config is None:
        logmessage("Ignoring call to digits because Twilio not enabled")
        return Response(str(resp), mimetype='text/xml')
    if "AccountSid" not in request.form or request.form["AccountSid"] != twilio_config['name']['default'].get('account sid', None):
        logmessage("Request to digits did not authenticate")
        return Response(str(resp), mimetype='text/xml')
    if "Digits" in request.form:
        the_digits = re.sub(r'[^0-9]', '', request.form["Digits"])
        logmessage("digits: got " + str(the_digits))
        phone_number = r.get('da:callforward:' + str(the_digits))
        if phone_number is None:
            resp.say(word("I am sorry.  The code you entered is invalid or expired.  Goodbye."))
            resp.hangup()
        else:
            dial = resp.dial(number=phone_number)
            r.delete('da:callforward:' + str(the_digits))
    else:
        logmessage("digits: no digits received")
        resp.say(word("No access code was entered."))
        resp.hangup()
    return Response(str(resp), mimetype='text/xml')

@app.route("/sms", methods=['POST'])
def sms():
    resp = twilio.twiml.Response()
    if twilio_config is None:
        logmessage("Ignoring call to digits because Twilio not enabled")
        return Response(str(resp), mimetype='text/xml')
    if "AccountSid" not in request.form or request.form["AccountSid"] not in twilio_config['account sid']:
        logmessage("Request to digits did not authenticate")
        return Response(str(resp), mimetype='text/xml')
    logmessage(str(request.form))
    return Response(str(resp), mimetype='text/xml')

docassemble.base.functions.set_chat_partners_available(chat_partners_available)

r = redis.StrictRedis(host=docassemble.base.util.redis_server, db=0)

if not in_celery:
    import docassemble.webapp.worker
    #sys.stderr.write("calling set worker now\n")
    docassemble.base.functions.set_worker(docassemble.webapp.worker.background_action)
import docassemble.webapp.machinelearning
docassemble.base.util.set_knn_machine_learner(docassemble.webapp.machinelearning.SimpleTextMachineLearner)
