# -*- coding: utf-8 -*-

from flask import Blueprint
from flask import Response
from flask import request
from flask import render_template
#from werzeug import secure_filename

from ..user import Device
from ..user import DoubanUser
from ..user import Bind
from ..shai import Post
from ..shai import Favor
from ..utils import jsonify
from ..utils import allowed_file

from ..extensions import beansdb

from .serializer import PostSerializer

from datetime import datetime
import hashlib
import sys

api = Blueprint('api', __name__, url_prefix='/api/v1')


@api.route('/geteid', methods=['GET'])
def getuid():
    try:
        eid = Device.gen_eid()
        return jsonify(ret = 0,
                    errcode = '0100',
                    errmsg='',
                    data = {'eid' : eid} )
    except Exception, e:
        return jsonify(ret = -1,
                    errcode = '0101',
                    errmsg = 'connect mysql server failed')


@api.route('/bind', methods=['POST'])
def bind():
    eid = request.form.get('eid')
    uid = request.form.get('uid')
    name = request.form.get('name')
    avatar = request.files.get('avatar')
    alt = request.form.get('alt')
    join_time = request.form.get('join_time')
    loc_id = request.form.get('loc_id')
    loc_name = request.form.get('loc_name')

    if not eid or not uid or not name or not avatar or not alt:
        return jsonify(ret = -1,
                errcode = '0201',
                errmsg = 'eid, uid, name, avatar or alt is none')
    
    filename = avatar.filename
    if not allowed_file(filename):
        return jsonify(ret = -1,
                    errcode = '0202',
                    errmsg = 'not support image type')
    
    try:
        douban_user = DoubanUser.get_by_uid(uid)
        if not douban_user:
            type = filename.split('.')[1].lower().encode('utf8', 'ignore')
            avatar_name = "%s/%s/%s" %("avatar", uid, filename)
            avatar_id = hashlib.new('md5', avatar_name).hexdigest() + "." + type
            data = {'image':avatar.stream.read(), 'mime':avatar.mimetype}
            beansdb.set(avatar_id, data)
            DoubanUser.add(uid, name, avatar_id, alt, 1, join_time, loc_id, loc_name)
        bind = Bind.get(eid, uid)
        if not bind:
            Bind.add(eid, uid)
        return jsonify(ret = 0,
                    errcode = '0200',
                    errmgs = '')
    except Exception, e:
        print e
        return jsonify(ret = -1,
                    errcode = '0202',
                    errmsg = 'connect database server failed')


@api.route('/shai', methods=['POST'])
def shai():
    uid = request.form.get('uid')
    content = request.form.get('content')
    image = request.files.get('image')
    if not uid or not content or not image:
        return jsonify(ret = -1,
                    errcode = '0301',
                    errmsg = 'uid, content or image is null')

    filename = image.filename
    if not allowed_file(filename):
        return jsonify(ret = -1,
                    errcode = '0302',
                    errmsg = 'not support image type')

    try:
        type = filename.split('.')[1].lower().encode('utf8', 'ignore')
        image_name = "%s/%s/%s" %("image", uid, filename)
        image_id = hashlib.new('md5', image_name).hexdigest() + "." + type
        small_image_id = image_id
        data = {'image':image.stream.read(), 'mime':image.mimetype}
        beansdb.set(image_id, data)
        id = Post.add(uid, content, image_id, small_image_id)
        post = Post.get(id)
        user_douban = DoubanUser.get_by_uid(post.uid)
        post.user_douban = user_douban
        return jsonify(ret = 0,
                    errcode = '0300',
                    errmgs = '',
                    data = PostSerializer(post).data)
    except Exception, e:
        print e
        return jsonify(ret = -1,
                    errcode = '0302',
                    errmsg = 'connect mysql server failed')


@api.route('/latest', methods=['GET'])
def latest():
    eid = int(request.args.get('eid', -1))
    max_id = int(request.args.get('max_id', 0))
    count = int(request.args.get('count', 20))
    gender = int(request.args.get('gender', 0))
    posts = Post.get_latest(max_id, count)
    nextstartpos = sys.maxint

    for post in posts:
        if nextstartpos >  post.id:
            nextstartpos = post.id
        user_douban = DoubanUser.get_by_uid(post.uid)
        post.user_douban = user_douban

    return jsonify(ret = 0,
                errcode = '0400',
                errmsg = '',
                data = {'nextstartpos' : nextstartpos,
                    "shais": PostSerializer(posts, many=True).data,})


@api.route('/praise', methods=['POST'])
def praise():
    uid = request.form.get('uid')
    post_id = request.form.get('post_id')
    print uid, post_id
    if not uid or not post_id:
        return jsonify(ret = -1,
                    errcode = '0501',
                    errmsg = 'uid, post_id is null')
    try:
        favor = Favor.is_favored(uid, post_id)
        if favor:
            return jsonify(ret = -1,
                    errcode = '0502',
                    errmsg = 'uid had been praised id')
        else:
            Favor.add(uid, post_id)
            return jsonify(ret = -1,
                    errcode = '0500',
                    errmsg = '')
    except Exception, e:
        print e
        return jsonify(ret = -1,
                    errcode = '0503',
                    errmsg = 'connect database server failed')

