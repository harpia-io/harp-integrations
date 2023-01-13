import traceback
from microservice_template_core import db
import datetime
import ujson as json
from microservice_template_core.tools.logger import get_logger
from marshmallow import Schema, fields

logger = get_logger()


class Integrations(db.Model):
    __tablename__ = 'configured_integrations'

    integration_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    integration_key = db.Column(db.VARCHAR(70), nullable=True, unique=True)
    integration_name = db.Column(db.VARCHAR(70), nullable=True, unique=False)
    integration_type = db.Column(db.VARCHAR(70), nullable=True, unique=False)
    status = db.Column(db.VARCHAR(70), nullable=True, unique=False)
    config = db.Column(db.Text(4294000000), default='{}')
    create_ts = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow(), nullable=False)
    last_update_ts = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow(), nullable=False)

    def __repr__(self):
        return f"{self.integration_id}_{self.integration_name}"

    def dict(self):
        return {
            'integration_id': self.integration_id,
            'integration_key': self.integration_key,
            'integration_name': self.integration_name,
            'integration_type': self.integration_type,
            'config': json.loads(self.config),
            'status': self.status,
            'create_ts': self.create_ts,
            'last_update_ts': self.last_update_ts
        }

    @classmethod
    def create_integration(cls, data):
        exist_integration_name = cls.query.filter_by(integration_name=data['integration_name'], integration_type=data['integration_type']).one_or_none()
        if exist_integration_name:
            raise ValueError(f"Integration Name: {data['integration_name']} and Type: {data['integration_type']} already exist")
        new_obj = Integrations(
            integration_name=data['integration_name'],
            integration_key=data['integration_key'],
            integration_type=data['integration_type'],
            status=data['status'],
            config=json.dumps(data['config']),
        )
        new_obj = new_obj.save()
        return new_obj

    @classmethod
    def obj_exist(cls, env_id=None, integration_key=None):
        if env_id:
            return cls.query.filter_by(integration_id=env_id).one_or_none()

        if integration_key:
            return cls.query.filter_by(integration_key=integration_key).one_or_none()

    def update_obj(self, data, integration_id):
        if 'config' in data:
            data['config'] = json.dumps(data['config'])

        self.query.filter_by(integration_id=integration_id).update(data)

        db.session.commit()

    def integration_info_dict(self):
        return {
            'integration_id': self.integration_id,
            'integration_name': self.integration_name,
            'integration_type': self.integration_type,
            'integration_key': self.integration_key,
            'config': json.loads(self.config),
            'status': self.status
        }

    @classmethod
    def get_all_integrations(cls):
        get_all_integrations = cls.query.filter_by().all()
        all_integrations = [single_event.integration_info_dict() for single_event in get_all_integrations]

        return all_integrations

    def save(self):
        try:
            db.session.add(self)
            db.session.flush()
            db.session.commit()

            return self
        except Exception as exc:
            logger.critical(
                msg=f"Can't commit changes to DB \nException: {str(exc)} \nTraceback: {traceback.format_exc()}",
                extra={'tags': {}}
            )
            db.session.rollback()

    def delete_obj(self):
        db.session.delete(self)
        db.session.commit()


class IntegrationsSchema(Schema):
    integration_id = fields.Int(dump_only=True)
    integration_name = fields.Str(required=True)
    integration_key = fields.Str(required=False)
    integration_type = fields.Str(required=True)
    status = fields.Str(required=True)
    config = fields.Dict(
        environment_id=fields.Int(required=True),
        scenario_id=fields.Int(required=True)
    )
    create_ts = fields.DateTime("%Y-%m-%d %H:%M:%S", dump_only=True)
    last_update_ts = fields.DateTime("%Y-%m-%d %H:%M:%S", dump_only=True)