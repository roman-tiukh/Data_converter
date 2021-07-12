import os
from django.conf import settings


class Savepoint:
    def __init__(self, file_name: str, type=int):
        self.cast = type
        file_dir = os.path.join(settings.BASE_DIR, 'save_points')
        os.makedirs(file_dir, exist_ok=True)
        self.file_path = os.path.join(file_dir, f'{file_name}.txt')
        # create file if not exists
        if not os.path.exists(self.file_path):
            open(self.file_path, 'w').close()

        self.saved_objects = set()
        with open(self.file_path, 'r') as file:
            for line in file:
                self.saved_objects.add(self.cast(line.strip()))
        self.file = open(self.file_path, 'a')

    def has(self, nacp_declarant_id):
        return self.cast(nacp_declarant_id) in self.saved_objects

    def add(self, object_id):
        if not self.has(object_id):
            self.file.write(f'{object_id}\n')
            self.saved_objects.add(self.cast(object_id))

    def close(self):
        self.file.close()
