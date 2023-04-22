import wow_api


class BlizzardApi:
    """Blizzard API class.

    Attributes:
        client_id: A string client id supplied by Blizzard.
        client_secret: A string client secret supplied by Blizzard.
    """

    def __init__(self, client_id, client_secret):
        """Init BlizzardApi."""
        self.wow = wow_api.WowApi(client_id, client_secret)
