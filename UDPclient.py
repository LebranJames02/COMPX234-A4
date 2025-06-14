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

    def send_and_receive(self, sock: socket.socket, message: str,
                         dest_addr: Tuple[str, int]) -> Optional[str]:
        """发送消息并接收响应，包含超时重传机制"""
        current_timeout = self.initial_timeout
        retries = 0