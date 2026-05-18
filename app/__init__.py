from flask import Flask
from flasgger import Swagger
from app.database import db
from app.config import config_map


def create_app(env="development"):
    app = Flask(__name__)
    cfg = config_map.get(env, config_map["development"])
    app.config.from_object(cfg)

    db.init_app(app)

    swagger_config = {
        "headers": [],
        "specs": [{"endpoint": "apispec", "route": "/api/docs/apispec.json"}],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/api/docs",
    }
    Swagger(app, config=swagger_config, template={
        "info": {"title": "Kanban QA Automation API", "version": "1.0"},
        "securityDefinitions": {
            "Bearer": {"type": "apiKey", "name": "Authorization", "in": "header"}
        },
    })

    from app.auth.routes import auth_bp
    from app.boards.routes import boards_bp
    from app.cards.routes import cards_bp
    from app.users.routes import users_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(boards_bp)
    app.register_blueprint(cards_bp)
    app.register_blueprint(users_bp)

    # UI views
    from app.views import views_bp
    app.register_blueprint(views_bp)

    with app.app_context():
        db.create_all()

    return app
