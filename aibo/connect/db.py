import json

class JsonController:
    def __init__(self, filename="conversation_history.json"):
        self.filename = filename
    def read_conversations_history(self, filename=""):
        if filename == "":
            filename = self.filename
        with open(filename, "r") as f:
            conversations = json.load(f)
            self.conversations = conversations
        return self.conversations
    def write_conversations_history(self, conversations, filename=""):
        if filename == "":
            filename = self.filename
        with open(filename, "w") as f:
            json.dump(conversations, f)
    def update_conversations(self, conversation, user_id=""):
        conversations = self.read_conversations_history()
        conversations[user_id] = conversation
        self.write_conversations_history(conversations)