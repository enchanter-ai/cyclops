from enum import StrEnum

class Server(StrEnum):
    FILESYSTEM = "filesystem"
    WEB = "web"
    NOTIFY = "notify"
