import socket
import sys
import os
import base64
import time
import threading
from typing import Tuple, Optional

class UDPClient:
    def __init__(self, server_host: str, server_port: int, download_list: str):
        self.server_host = server_host
        self.server_port = server_port
        self.download_list = download_list
        self.buffer_size = 1024
        self.max_retries = 5
        self.initial_timeout = 1.0  # 初始超时时间（秒）