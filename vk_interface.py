import vk_config
from vk_api import VkApi
from vk_api.longpoll import VkLongPoll
from vk_api.utils import get_random_id


class VkBotInterface:
  
    def __init__(self):
        self.community_token = vk_config.community_token
        self.vk_session = VkApi(token=self.community_token)
        self.longpoll = VkLongPoll(self.vk_session)

    def message_send(self, user_id, message, attachment=None):
    
        self.vk_session.method('messages.send',
                               {'user_id': user_id,
                                'message': message,
                                'attachment': attachment,
                                'random_id': get_random_id()
                                }
                               )
