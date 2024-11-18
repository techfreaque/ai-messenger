import logging
from typing import TYPE_CHECKING, Callable, TypedDict, TypeVar, cast

from flask import jsonify, redirect, request, url_for
from flask.typing import ResponseReturnValue
from flask_login import login_required  # type: ignore
from flask_login import login_user  # type: ignore
from flask_login import (  # type: ignore
    LoginManager,
    UserMixin,
    current_user,
    logout_user,
)

from app.lib.logger import setup_logger

if TYPE_CHECKING:
    from app.lib.bot_manager import BotManager


class UserLogin(TypedDict):
    password: str | None


class User(UserMixin):
    def __init__(self, id: str):
        self.id = id


# Define a generic callable type
F = TypeVar('F', bound=Callable[..., ResponseReturnValue])


class WebLoginManager:
    login_manager: LoginManager
    dev_mode: bool = True

    def init_login(self, bot: "BotManager"):
        path_prefix = "/api"
        self.login_manager = LoginManager(bot.web_server.app)
        self.login_manager.login_view = (  # type: ignore
            'login'  # Redirect to login if unauthorized
        )
        self.logger = setup_logger(
            "BotManager",
            logging.DEBUG,
        )

        @self.login_manager.user_loader  # type: ignore
        def load_user(user_id: str) -> User | None:  # type: ignore
            return User(user_id) if user_id == "admin" else None

        @bot.web_server.app.route(f'{path_prefix}/auth-check', methods=['GET'])
        def auth_check():  # type: ignore
            if current_user.is_authenticated or self.dev_mode:
                return jsonify({"logged_in": True}), 200

            else:
                return jsonify({"logged_in": False}), 200

        # Login Route
        @bot.web_server.app.route(f'{path_prefix}/login', methods=['POST'])
        def login():  # type: ignore
            data = request.json
            if data is None:
                return (
                    jsonify({"success": False, "error": "Invalid input"}),
                    400,
                )
            user_data: UserLogin = data
            if user_data['password'] == '1':  # Simple check
                self.logger.info("Successful login")
                user = User(id='admin')
                login_user(user)
                return jsonify({"success": True}), 200
            self.logger.info("Failed login")
            return jsonify({"success": False}), 401

        # Logout Route
        @bot.web_server.app.route(f'{path_prefix}/logout')
        @login_required
        def logout():  # type: ignore
            logout_user()
            return redirect(url_for('login'))

    def conditional_login_required(
        self,
    ) -> Callable[[F], F]:
        """Decorator that applies @login_required only if login_manager.dev_mode is False."""

        def decorator(func: F) -> F:
            if self.dev_mode:
                # Directly return the function if dev_mode is True, skipping @login_required
                return func
            else:
                # Otherwise, apply @login_required
                return cast(
                    F, login_required(func)
                )  # Type cast for compatibility

        return decorator
