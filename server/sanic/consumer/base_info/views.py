# -*- coding: utf-8 -*-
# @Time     : 5/6/19 7:02 PM
# @Author   : Lee才晓
# @Describe :
from sanic import Blueprint
from bson import json_util
from sanic.exceptions import abort
from sanic.request import Request
from sanic_jwt_extended.tokens import Token

from consumer.base_info.models import ConsumerBaseInfo, ReceivingAddress
from system.response import *
from sanic_jwt_extended import create_access_token

from utils.decorator.exception import response_exception

blueprint = Blueprint(name="base_info", url_prefix='/base_info', version=1)


@blueprint.route(uri='/create/info', methods=['POST'])
async def create_consumer_info(request):
    """创建消费者账号信息"""
    """参数(nickname,password,email,mobile,avatar,gender,birthday,intro)"""
    params = request.json
    consumer = ConsumerBaseInfo.init_base_info(**params)

    if not consumer.check_params_is_none(except_list=['consumer_code', 'create_time',
                                                      'verify_id', 'receiving_address',
                                                      'third_party_info']):
        abort(status_code=ParamsErrorCode)

    old_info = await consumer.find_consumer_by_mobile_or_nickname()
    if old_info:
        abort(status_code=ExistsErrorCode, message='账号已存在')

    consumer_code = consumer.create_consumer_info()

    if consumer_code:
        abort(status_code=JsonSuccessCode, message=consumer_code)
    else:
        abort(status_code=ServerErrorCode, message='账号创建失败')


@blueprint.route(uri='/sign/in', methods=['POST'])
async def consumer_sign_in(request):
    """消费者登录接口"""
    """参数(account, password)"""

    params = request.json

    account = params.get('account', '')
    password = params.get('password', '')

    if not all([account, password]):
        abort(status_code=ParamsErrorCode)

    consumer = ConsumerBaseInfo.init_base_info(**params)

    consumer_info = await consumer.get_consumer_pwd()
    if not consumer_info:
        abort(status_code=NoExistsErrorCode, message='当前账号不存在')

    if consumer.check_consumer_password(old_pwd=consumer_info['password'], new_pwd=password):
        token = await create_access_token(app=request.app, identity='nickname',
                                          user_claims=json_util.dumps(consumer_info))

        abort(status_code=JsonSuccessCode, message={'token': token, 'consumer_code': consumer_info['consumer_code']})
    else:
        abort(status_code=UnAuthorizedCode, message='账号或密码错误')


@blueprint.route(uri='/get/info', methods=['POST'])
@response_exception
async def get_consumer_base_info(request: Request, token: Token):
    """获取消费者的基本信息"""
    """参数(mobile, nickname, consumer_code)"""
    params = request.json

    consumer_code = params.get('consumer_code', '')

    consumer = ConsumerBaseInfo.init_base_info(**params)

    if consumer_code:
        consumer_info = await consumer.find_consumer_by_consumer_code()
    else:
        consumer_info = await consumer.find_consumer_by_mobile_or_nickname()

    if not consumer_info:
        abort(status_code=NoExistsErrorCode, message='当前账号不存在')

    abort(status_code=JsonSuccessCode, message=consumer_info)


@blueprint.route(uri='/add/receive/address', methods=['POST'])
@response_exception
async def add_consumer_receive_address(request: Request, token: Token):
    """添加消费者收货地址"""
    """参数(consumer_code, address, region_code, mobile, contacts)"""

    params = request.json

    consumer_code = params.get('consumer_code', '')

    receive_address = ReceivingAddress.init_receiving_address(**params)
    if not all([receive_address, consumer_code, receive_address.check_params_is_none()]):
        abort(status_code=ParamsErrorCode)

    consumer = ConsumerBaseInfo.init_base_info(consumer_code=consumer_code)
    add_result = await consumer.add_consumer_receive_address(receive_address)
    if add_result.modified_count:
        abort(status_code=JsonSuccessCode, message='添加收货地址成功')
    abort(status_code=ServerErrorCode, message='添加收货地址失败')


@blueprint.route(uri='/remove/receive/address', methods=['POST'])
@response_exception
async def remove_consumer_receive_address(request: Request, token: Token):
    """移除消费者收货地址"""
    """参数(consumer_code, address, region_code, mobile, contacts)"""

    params = request.json

    consumer_code = params.get('consumer_code', '')

    receive_address = ReceivingAddress.init_receiving_address(**params)
    if not all([receive_address, consumer_code, receive_address.check_params_is_none()]):
        abort(status_code=ParamsErrorCode)

    consumer = ConsumerBaseInfo.init_base_info(consumer_code=consumer_code)
    remove_result = await consumer.remove_consumer_receiver_address(receive_address)
    if remove_result.modified_count:
        abort(status_code=JsonSuccessCode, message='移除收货地址成功')
    abort(status_code=ServerErrorCode, message='移除收货地址失败')


@blueprint.route(uri='/get/receive/address', methods=['POST'])
@response_exception
async def get_consumer_receiver_address(request: Request, token: Token):
    """获取消费者收货地址"""
    """参数(consumer_code)"""

    params = request.json

    consumer_code = params.get('consumer_code', '')

    if not consumer_code:
        abort(status_code=ParamsErrorCode)

    consumer = ConsumerBaseInfo.init_base_info(consumer_code=consumer_code)
    address_list = await consumer.get_consumer_receiver_address()

    abort(status_code=JsonSuccessCode, message=address_list)
