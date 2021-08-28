from datetime import datetime
import os


class LoadingLogger:
    def __init__(self, directory: str):
        self.log_dir = os.path.join(directory, datetime.now())
        create_directory(self.log_dir)
        super().__init__()

    def log_loading(self, process_id, message):
        log_file_name = f"{str(process_id)}.log"
        message = message+"\n"
        with open(f"{self.log_dir}/{log_file_name}", "a+") as log_file:
            log_file.write(message)


def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
