"""Chainbot IPC."""
import json
import functools


def _ipc_call(call_type: str, **kwargs):
    """IPC call wrapper"""
    return json.dumps((call_type, kwargs))


def ipc_call(**default_options):
    """IPC call."""

    def wrapper(func):
        @functools.wraps(func)
        def wrapped(**kwargs):
            # Some fancy boo stuff
            default_options.update(kwargs)
            data = _ipc_call(func.__name__, **default_options)
            ret = func(data=data, **default_options)
            if ret is None:
                return data

        return wrapped

    return wrapper


class ScoreboardIPCClient:
    """IPC Client."""

    @staticmethod
    def do_ipc_call(call_type, **kwargs):
        """Call."""
        if not hasattr(ScoreboardIPCClient, call_type):
            raise RuntimeError("invalid call type: {}".format(call_type))
        function = getattr(ScoreboardIPCClient, call_type)
        return function(**kwargs)

    @staticmethod
    @ipc_call()
    def game_can_start(**kwargs):
        """Get whether game can be started."""

    @staticmethod
    @ipc_call()
    def score_status(**kwargs):
        """Get score data."""

    @staticmethod
    @ipc_call()
    def player_status(**kwargs):
        """Get player data."""

    @staticmethod
    @ipc_call()
    def tournament_active(**kwargs):
        """Get tournament status."""

    @staticmethod
    @ipc_call(tournament_id=0)
    def activate_tournament(**kwargs):
        """Activate tournament."""

    @staticmethod
    @ipc_call()
    def deactivate_tournament(**kwargs):
        """Deactivate tournament."""

    @staticmethod
    @ipc_call()
    def activate_game(**kwargs):
        """Actvivate game."""

    @staticmethod
    @ipc_call()
    def update_registry(**kwargs):
        """Update registry."""

    @staticmethod
    @ipc_call(registry_id="player")
    def retrieve_registry(**kwargs):
        """Retrieve registry data."""

    @staticmethod
    @ipc_call()
    def game_begin(**kwargs):
        """Start game."""

    @staticmethod
    @ipc_call()
    def game_end(**kwargs):
        """Stop game."""

    @staticmethod
    @ipc_call(player_number=0)
    def remote_pair(**kwargs):
        """Pair remote."""

    @staticmethod
    @ipc_call(player_number=0)
    def remote_unpair(**kwargs):
        """Unpair remote."""

    @staticmethod
    @ipc_call(web_txt="", panel_txt="")
    def player_register(**kwargs):
        """Register player."""

    @staticmethod
    @ipc_call(player_number=0)
    def player_unregister(**kwargs):
        """Unregister player."""

    @staticmethod
    @ipc_call(evt_type="", player_num=0)
    def score_event(**kwargs):
        """Scoring event."""

    @staticmethod
    @ipc_call(player_num=0)
    def set_turn(**kwargs):
        """Set turn."""

    @staticmethod
    @ipc_call(player_num=0, score=0)
    def set_score(**kwargs):
        """Set score."""

    @staticmethod
    @ipc_call()
    def game_status(**kwargs):
        """Get game status."""
