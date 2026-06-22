import os

class FileTool:

    @staticmethod
    def list_directory(path):

        return os.listdir(
            os.path.expanduser(path)
        )

    @staticmethod
    def read_file(path):

        with open(path,"r") as f:
            return f.read()

    @staticmethod
    def create_folder(path):

        os.makedirs(path,exist_ok=True)

        return "Folder Created"