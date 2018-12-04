from ruamel.yaml import YAML
import os

yaml = YAML(typ='safe')
yaml.default_flow_style = False
yaml.sort_base_mapping_type_on_output = False

def _load_yaml_file(filepath):
    with open(filepath, 'r') as stream:
        try:
            return yaml.load(stream)
        except yaml.YAMLError as err:
            raise ValueError(*err.args)

def _dump_yaml_file(filepath, data):
    with open(filepath, 'w') as stream:
        try:
            return yaml.dump(data, stream)
        except yaml.YAMLError as err:
            raise ValueError(*err.args)

class Db:
    def __init__(self):
        self.__series_db = []

    def load_series(self, dirpath):
        print('TODO: load series database', dirpath)

    def load_series_v0(self, dirpath):
        filepath = os.path.join(dirpath, '.showlist')
        if not os.path.isfile(filepath):
            raise ValueError('database does not exist in this directory')

        with open(filepath, 'r') as fp:
            for _, line in enumerate(fp):
                line = line.rstrip('\n')
                video_data = {}
                if line[0] == '*':
                    start = 'sometime'
                    space_idx = line.index(' ')
                    if line[1] != ' ':
                        start = line[1:space_idx].replace('-', '/').replace('~', ' ')
                    video_file = line[space_idx + 1:]
                    video_data['video'] = video_file
                    video_data['viewings'] = [ { 'start': start, 'end': 'sometime at finished?' } ]
                else:
                    video_data['video'] = line
                self.add_show_to_series(video_data)

    def add_show_to_series(self, video_data):
        self.__series_db.append(video_data)

    def write_series(self, dirpath):
        filepath = self.get_series_db_path(dirpath)
        _dump_yaml_file(filepath, self.__series_db)

    def get_series_db_path(self, dirpath):
        return os.path.join(dirpath, '.showlist.yaml')

