# -*- coding: utf-8 -*-
# @Time     : 6/17/19 7:23 PM
# @Author   : Lee才晓
# @Describe :
from sanic import Blueprint
from sanic.exceptions import abort
from sanic.request import Request
from sanic_jwt_extended.tokens import Token

from coupon.models import Coupon
from system.response import ParamsErrorCode, ExistsErrorCode, JsonSuccessCode, ServerErrorCode, NoExistsErrorCode
from utils.decorator.exception import response_exception

blueprint = Blueprint(name="coupon", version=1)


@blueprint.route(uri='/create/info', methods=['POST'])
@response_exception
async def create_coupon_info(request: Request, token: Token):
    """
    :name create_coupon_info
    :param (title/start_time/end_time/explain/total_num/distribution_form_type/distribution_form_value
            use_threshold/available_product_type/available_product_list/limit_num/consumer_type
            consumer_value/available_org_type/available_org_list)
    """
    params = request.json

    coupon = Coupon.init_coupon_info(**params)

    if not all([coupon.check_params_is_none(
            ['coupon_code', 'available_product_list', 'available_org_list', 'consumer_value',
             'create_time', 'used_num', 'received_num', 'vail_status'])]):
        abort(status_code=ParamsErrorCode)

    is_exists = await coupon.find_coupon_by_title()
    if is_exists and is_exists['coupon_code'] != coupon.coupon_code:
        abort(status_code=ExistsErrorCode, message='优惠券标题已存在')

    coupon_code = coupon.create_coupon_info()
    if coupon_code:
        abort(status_code=JsonSuccessCode, message={'coupon_code': coupon_code})

    abort(status_code=ServerErrorCode, message='优惠券创建失败')


@blueprint.route(uri='/update/info', methods=['POST'])
@response_exception
async def update_coupon_info(request: Request, token: Token):
    """
    :name update_coupon_info
    :param (coupon_code/title/start_time/end_time/explain/total_num/distribution_form_type/distribution_form_value
            use_threshold/available_product_type/available_product_list/limit_num/consumer_type
            consumer_value/available_org_type/available_org_list)
    """
    params = request.json

    coupon = Coupon.init_coupon_info(**params)

    if not coupon.check_params_is_none(['available_product_list', 'available_org_list', 'consumer_value',
                                        'create_time', 'used_num', 'received_num', 'vail_status']):
        abort(status_code=ParamsErrorCode)

    coupon_info = await coupon.find_coupon_by_coupon_code()
    if not coupon_info:
        abort(status_code=NoExistsErrorCode, message='优惠券标题不存在')

    result = await coupon.update_coupon_info()
    if result.modified_count or result.matched_count:
        abort(status_code=JsonSuccessCode, message='优惠券更新成功')
    abort(status_code=ServerErrorCode, message='优惠券更新失败')


@blueprint.route(uri='/delete/info', methods=['POST'])
@response_exception
async def delete_coupon_info(request: Request, token: Token):
    """
    :name delete_coupon_info
    :param (coupon_code)
    """
    params = request.json

    coupon = Coupon.init_coupon_info(**params)
    if not coupon.coupon_code:
        abort(status_code=ParamsErrorCode)

    result = await coupon.delete_coupon_by_coupon_code()
    if result.raw_result and result.raw_result.ok:
        abort(status_code=JsonSuccessCode, message='the coupon delete success')

    abort(status_code=ServerErrorCode, message='the coupon delete failed')
