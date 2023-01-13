from microservice_template_core.tools.flask_restplus import api
from flask_restx import Resource
import traceback
from microservice_template_core.tools.logger import get_logger
from harp_integrations.models.available_integrations import Integrations, IntegrationsSchema
from flask import request
from werkzeug.exceptions import BadRequest
from microservice_template_core.decorators.auth_decorator import token_required

logger = get_logger()
ns = api.namespace('api/v1/integrations/available', description='Harp All available integrations endpoints')
integrations = IntegrationsSchema()


@ns.route('')
class CreateIntegration(Resource):
    @staticmethod
    @api.response(200, 'Integration has been created')
    @api.response(400, 'Integration already exist')
    @api.response(500, 'Unexpected error on backend side')
    @token_required()
    def put():
        """
        Create Available Integration directly via API
        Use this method to create Available Integration directly via API
        * Send a JSON object
        ```
            {
                "name": "Zabbix",
                "status": "active",
                "website_url": "http://zabbix.com"
            }
        ```
        """
        try:
            data = integrations.load(request.get_json())
            new_obj = Integrations.create_integration(data)
            result = integrations.dump(new_obj.dict())
        except ValueError as val_exc:
            logger.warning(
                msg=str(val_exc),
                extra={'tags': {}})
            return {"msg": str(val_exc)}, 400
        except Exception as exc:
            logger.critical(
                msg=f"General exception \nException: {str(exc)} \nTraceback: {traceback.format_exc()}",
                extra={'tags': {}})
            return {'msg': 'Exception raised. Check logs for additional info'}, 500

        return result, 200


@ns.route('/<integration_id>')
class UpdateIntegration(Resource):
    @staticmethod
    @api.response(200, 'Integration has been update')
    @api.response(400, 'Integration already exist')
    @api.response(500, 'Unexpected error on backend side')
    @token_required()
    def post(integration_id):
        """
        Update existing Integration
        Use this method to update existing Integration directly via API
        * Send a JSON object
        ```
            {
                "name": "Zabbix",
                "status": "active",
                "website_url": "http://zabbix.com"
            }
        ```
        """
        if not integration_id:
            return {'msg': 'integration_id should be specified'}, 404
        obj = Integrations.obj_exist(integration_id)
        if not obj:
            return {'msg': f'Integration with specified id - {integration_id} is not exist'}, 404
        try:
            data = integrations.load(request.get_json())
            obj.update_obj(data, integration_id=integration_id)
            result = integrations.dump(obj.dict())
        except ValueError as val_exc:
            logger.warning(
                msg=f"Integration updating exception \nException: {str(val_exc)} \nTraceback: {traceback.format_exc()}",
                extra={'tags': {}})
            return {"msg": str(val_exc)}, 400
        except BadRequest as bad_request:
            logger.warning(
                msg=f"Integration updating exception \nException: {str(bad_request)} \nTraceback: {traceback.format_exc()}",
                extra={'tags': {}})
            return {'msg': str(bad_request)}, 400
        except Exception as exc:
            logger.critical(
                msg=f"Integration updating exception \nException: {str(exc)} \nTraceback: {traceback.format_exc()}",
                extra={'tags': {}})
            return {'msg': 'Exception raised. Check logs for additional info'}, 500
        return result, 200

    @staticmethod
    @token_required()
    def get(integration_id):
        """
            Return Integrations object with specified id
        """
        if not integration_id:
            return {'msg': 'integration_id should be specified'}, 404
        obj = Integrations.obj_exist(integration_id)
        if not obj:
            return {'msg': f'object with integration_id - {integration_id} is not found'}, 404
        result = integrations.dump(obj.dict())
        return result, 200

    @staticmethod
    @token_required()
    def delete(integration_id):
        """
            Delete Integration object with specified id
        """
        if not integration_id:
            return {'msg': 'integration_id should be specified'}, 404
        obj = Integrations.obj_exist(integration_id)
        try:
            if obj:
                obj.delete_obj()
                logger.info(
                    msg=f"Environment deletion. Id: {integration_id}",
                    extra={})
            else:
                return {'msg': f'Object with specified integration_id - {integration_id} is not found'}, 404
        except Exception as exc:
            logger.critical(
                msg=f"Environment deletion exception \nException: {str(exc)} \nTraceback: {traceback.format_exc()}",
                extra={'tags': {}})
            return {'msg': f'Deletion of environment with id: {integration_id} failed. '
                           f'Exception: {str(exc)}'}, 500
        return {'msg': f"Environment with id: {integration_id} successfully deleted"}, 200


@ns.route('/all')
class AllAvailableIntegrations(Resource):
    @staticmethod
    @api.response(200, 'Info has been collected')
    @token_required()
    def get():
        """
        Return All exist Integrations
        """
        new_obj = Integrations.get_all_integrations()

        result = {'integrations': new_obj}

        return result, 200
