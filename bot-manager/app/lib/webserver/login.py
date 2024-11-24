import logging
from typing import TYPE_CHECKING, Any, Callable, TypedDict, TypeVar, cast

from flask import request
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


class UserLoginRequest(TypedDict):
    password: str | None


class User(UserMixin):
    def __init__(self, id: str):
        self.id = id


F = TypeVar('F', bound=Callable[..., Any])


class WebLoginManager:
    login_manager: LoginManager

    def __init__(self, dev_mode: bool) -> None:
        self.dev_mode: bool = False  #  dev_mode

    def init_login(self, bot: "BotManager") -> None:
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
            logged_in = cast(User, current_user).is_authenticated
            return {
                "loggedIn": logged_in,
                "requiresSetup": (
                    False
                    if bot.storage.bot_config.web_interface_api_key
                    else True
                ),
            }, 200

        @bot.web_server.app.route(f'{path_prefix}/login', methods=['POST'])
        def login() -> tuple[dict[str, None | bool | str], int]:  # type: ignore
            user_data = cast(
                UserLoginRequest,
                request.json,  # type: ignore
            )
            if (
                user_data
                and user_data['password']
                == bot.storage.bot_config.web_interface_api_key
            ) or not bot.storage.bot_config.web_interface_api_key:
                self.logger.info("Successful login")
                user = User(id='admin')
                login_user(user)
                self.logger.info("Web fronted logged in")
                return {"success": True}, 200
            self.logger.info("Failed login")
            return (
                {"success": False, "message": "Error: Wrong password"},
                200,
            )

        @bot.web_server.app.route(f'{path_prefix}/logout', methods=["GET"])
        @login_required
        def logout():  # type: ignore
            logout_user()
            self.logger.info("Web fronted logged out")
            return {"success": True}, 200

    def conditional_login_required(
        self,
    ) -> Callable[[F], F]:
        def decorator(func: F) -> F:
            if self.dev_mode:
                return func
            else:
                return cast(F, login_required(func))

        return decorator


class LoginResponse(TypedDict):
    success: bool
    requiresPasswordReset: bool | None
    message: str | None
