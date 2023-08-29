from uuid import uuid4 as gen_uuid


class Conversation:
    def __init__(self, prompt, user) -> None:
        self.messages = []
        self.prompt = prompt
        self.user = user


class Message:
    def __init__(self, content, uuid=None, prev_uuid=None) -> None:
        self.content = content
        self.feedback = None
        if uuid:
            self.uuid = uuid
        else:
            self.uuid = gen_uuid()

        self.prev_uuid = None
