from logging import StreamHandler
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


class PengfengNetworkHandler(StreamHandler):

    def emit(self, record):
        msg = self.format(record)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'logging',
            {
                'type': 'logging_info_message',
                'msg': msg
            }
        )
