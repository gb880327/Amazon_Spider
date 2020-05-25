#!python3
from flask import jsonify
from app.util.mm import multimethod


def render_json(data: object):
    return jsonify(data)


@multimethod(object, str)
def success(obj, msg='success'):
    return render_json({'code': 0, 'msg': msg, 'data': obj})


@multimethod(str)
def success(msg):
    return render_json({'code': 0, 'msg': msg})


@multimethod()
def success():
    return render_json({'code': 0, 'msg': 'success'})


@multimethod(int, str)
def error(code, msg):
    return render_json({'code': code, 'msg': msg})


@multimethod(str)
def error(msg):
    return render_json({'code': -1, 'msg': msg})


@multimethod()
def error():
    return render_json({'code': -1, 'msg': ''})
