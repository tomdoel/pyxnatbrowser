import configparser


class PropertyParser(object):

    def __init__(self, file_name):
        file = open(file_name, encoding="utf_8")
        parser = configparser.ConfigParser()
        parser.read_file(PropertyParser.add_section_header(file, 'properties'), source='my.props')
        self.properties = dict(parser['properties'])

    @staticmethod
    def add_section_header(properties_file, header_name):
        yield '[{}]\n'.format(header_name)
        for line in properties_file:
            yield line


