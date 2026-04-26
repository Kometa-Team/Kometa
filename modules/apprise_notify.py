import apprise as apprise_lib
from modules import util, webhooks
from modules.util import Failed

_PRIORITY_MAP = {
    1: apprise_lib.NotifyType.INFO,
    2: apprise_lib.NotifyType.INFO,
    3: apprise_lib.NotifyType.INFO,
    4: apprise_lib.NotifyType.SUCCESS,
    5: apprise_lib.NotifyType.FAILURE,
}


class AppriseNotify:
    def __init__(self, requests, params):  # requests unused; Apprise manages its own connections
        config_path = params["config"]
        # util.logger is None until Kometa initialises; guard allows tests to run without mocking
        if util.logger:
            util.logger.secret(config_path)
        self._apobj = apprise_lib.Apprise()
        ac = apprise_lib.AppriseConfig()
        ac.add(config_path)
        self._apobj.add(ac)
        if not len(self._apobj):
            raise Failed("Apprise Error: No valid notification services loaded from config")

    def notification(self, json):
        message, title, priority = webhooks.get_message(json)
        self._apobj.notify(
            title=title,
            body=message,
            notify_type=_PRIORITY_MAP.get(priority, apprise_lib.NotifyType.INFO),
        )
