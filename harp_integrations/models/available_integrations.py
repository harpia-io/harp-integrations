import traceback
from microservice_template_core import db
import datetime
from microservice_template_core.tools.logger import get_logger
from marshmallow import Schema, fields

logger = get_logger()


class Integrations(db.Model):
    __tablename__ = 'available_integrations'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.VARCHAR(70), nullable=True, unique=False)
    status = db.Column(db.VARCHAR(70), nullable=False, unique=False)
    website_url = db.Column(db.VARCHAR(254), nullable=False, unique=False)
    create_ts = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow(), nullable=False)
    last_update_ts = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow(), nullable=False)

    def __repr__(self):
        return f"{self.id}_{self.name}"

    def dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'status': self.status,
            'website_url': self.website_url,
            'create_ts': self.create_ts,
            'last_update_ts': self.last_update_ts
        }

    @classmethod
    def create_integration(cls, data):
        exist_integration_name = cls.query.filter_by(name=data['name']).one_or_none()
        if exist_integration_name:
            raise ValueError(f"Integration Name: {data['name']} already exist")
        new_obj = Integrations(
            name=data['name'],
            status=data['status'],
            website_url=data['website_url']
        )
        new_obj = new_obj.save()
        return new_obj

    @classmethod
    def obj_exist(cls, env_id):
        return cls.query.filter_by(id=env_id).one_or_none()

    def update_obj(self, data, integration_id):
        self.query.filter_by(id=integration_id).update(data)

        db.session.commit()

    def integration_info_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'status': self.status,
            'website_url': self.website_url
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
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    status = fields.Str(required=True)
    website_url = fields.Str(required=True)
    create_ts = fields.DateTime("%Y-%m-%d %H:%M:%S", dump_only=True)
    last_update_ts = fields.DateTime("%Y-%m-%d %H:%M:%S", dump_only=True)