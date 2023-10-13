import os
from datetime import datetime


class Log:
    def __init__(self, log_filename='mylog.log'):
        self.log_filename = log_filename
        self.logs_path = self.create_logs_directory()
        self.log_file_path = self.create_log_file()

    @staticmethod
    def create_logs_directory():
        logs_directory = 'logs'
        if not os.path.exists(logs_directory):
            os.makedirs(logs_directory)
        return logs_directory

    def create_date_directory(self):
        today_date = datetime.now().strftime("%Y-%m-%d")
        date_directory = os.path.join(self.logs_path, today_date)
        if not os.path.exists(date_directory):
            os.makedirs(date_directory)
        return date_directory

    def create_log_file(self):
        logs_path = self.create_date_directory()
        log_file_path = os.path.join(logs_path, self.log_filename)
        if not os.path.exists(log_file_path):
            with open(log_file_path, 'w'):
                pass
        return log_file_path

    def write(self, msg: str):
        with open(self.log_file_path, 'a') as log_file:
            log_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {msg}\n")
