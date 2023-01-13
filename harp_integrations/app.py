from microservice_template_core import Core
from microservice_template_core.settings import ServiceConfig, FlaskConfig, DbConfig
from harp_integrations.endpoints.available_integrations import ns as available_integrations
from harp_integrations.endpoints.configured_integrations import ns as configured_integrations
from harp_integrations.endpoints.health import ns as health


def main():
    ServiceConfig.configuration['namespaces'] = [available_integrations, configured_integrations, health]
    FlaskConfig.FLASK_DEBUG = False
    DbConfig.USE_DB = True
    app = Core()
    app.run()


if __name__ == '__main__':
    main()

