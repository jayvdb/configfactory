import os

from .abc import ConfigStore


class FileSystemConfigStore(ConfigStore):

    def __init__(self, directory: str):
        self.directory = directory
        os.makedirs(self.directory, exist_ok=True)

    def get_all_data(self) -> dict:

        settings = {}

        for root, dirs, files in os.walk(self.directory):

            if root == self.directory:
                for environment in dirs:
                    settings[environment] = {}

            else:
                directory, environment = os.path.split(root)
                if environment in settings and files:
                    for f in files:
                        component, extension = os.path.splitext(f)
                        if extension != '.json':
                            continue
                        with open(os.path.join(root, f)) as f:
                            settings[environment][component] = f.read()

        return settings

    def update_data(self, environment: str, component: str, data: str):
        os.makedirs(os.path.join(self.directory, environment), exist_ok=True)
        with open(os.path.join(self.directory, environment, f'{component}.json'), 'w') as fp:
            fp.write(data)

    def delete_data(self, environment: str, component: str):
        path = os.path.join(self.directory, environment, f'{component}.json')
        os.remove(path) if os.path.exists(path) else None
