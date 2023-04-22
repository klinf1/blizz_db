import game_data_api


class WowApi:
    """Wow API class.

    Attributes:
        client_id: A string client id supplied by Blizzard.
        client_secret: A string client secret supplied by Blizzard.
    """

    def __init__(self, client_id, client_secret):
        """Init WowApi."""
        self.game_data = game_data_api.WowGameDataApi(client_id, client_secret)
