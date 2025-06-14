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

        while retries <= self.max_retries:
            try:
                # 发送消息
                sock.sendto(message.encode(), dest_addr)
                print(f"发送: {message} 到 {dest_addr}")

                # 设置超时
                sock.settimeout(current_timeout)

                # 接收响应
                data, addr = sock.recvfrom(self.buffer_size * 10)
                response = data.decode().strip()
                print(f"接收: {response} 来自 {addr}")
                return response

            except socket.timeout:
                retries += 1
                print(f"超时 ({retries}/{self.max_retries}), 重传...")
                # 指数退避
                current_timeout *= 2
                if retries > self.max_retries:
                    print(f"重传次数超过限制，放弃请求")
                    return None

    def download_file(self, sock: socket.socket, filename: str,
                      data_port: int, file_size: int) -> bool:
        """分块下载文件"""
        print(f"开始下载文件: {filename}, 大小: {file_size} 字节")
        server_data_addr = (self.server_host, data_port)

        # 创建文件用于写入
        try:
            with open(filename, 'wb') as f:
                downloaded = 0
                block_size = self.buffer_size

                # 循环下载直到完成
                while downloaded < file_size:
                    end = min(downloaded + block_size - 1, file_size - 1)
                    request = f"FILE {filename} GET START {downloaded} END {end}"

                    response = self.send_and_receive(sock, request, server_data_addr)
                    if not response:
                        return False

                        # 解析响应
                        parts = response.split()
                        if parts[0] != "FILE" or parts[1] != filename or parts[2] != "OK":
                            print(f"错误响应: {response}")
                            return False

                        # 提取数据部分
                        data_index = parts.index("DATA") + 1
                        base64_data = " ".join(parts[data_index:])

                        try:
                            # Base64解码
                            binary_data = base64.b64decode(base64_data)
                            # 写入文件
                            f.seek(downloaded)
                            f.write(binary_data)
                            downloaded += len(binary_data)

                            # 显示进度
                            print("*", end="", flush=True)
                        except Exception as e:
                            print(f"数据解码错误: {e}")
                            return False

                print(f"\n文件 {filename} 下载完成")

        except Exception as e:
            print(f"文件操作错误: {e}")
            return False

            # 发送关闭请求
        close_request = f"FILE {filename} CLOSE"
        close_response = self.send_and_receive(sock, close_request, server_data_addr)

        if not close_response or "CLOSE_OK" not in close_response:
            print(f"关闭连接失败")
            return False

        print(f"文件 {filename} 连接已关闭")
        return True