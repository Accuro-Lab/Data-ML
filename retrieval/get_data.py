import os
import json
import glob

from utils import check_data_format


"""
Manifest object:
// Schema : manifest_object
// Purpose :
    Specifies file locations and documents to be included or excluded from
    the model. A file containing a single manifest_object is placed in
    the parent directory of the document store hierarchy.
{
  "include" : {
    "pathnames" : Array.of(String) // List of Unix relative paths (from the 
                                   // data directory). 
   }
  "exclude" : {
    "pathnames" : Array.of(String) // List of Unix relative paths (from the 
                                   // data directory). 
    "id" : Array.of(String)        // id of document to exclude
    "uri" : Array.of(String)       // URI of document to exclude
    "idSource" : Array.of(String)  // Exclude all docs published by source.
                                   // Overides the a potential "include *"
  }
}
"""

class DataFilter(object):
    """
    Object which filters the data according to the manifest
    file.
    """
    def __init__(self, manifest, additional_keys, verbose):
        self.ignore = {}
        self.ignore['id'] = manifest['exclude'].get('id', [])
        self.ignore['uri'] = manifest['exclude'].get('uri', [])
        self.ignore['idSource'] = manifest['exclude'].get('idSource', [])
        self.ignore_filenames = []
        for pathname in manifest['exclude'].get('pathnames', []):
            for filename in glob.glob(pathname):
                self.ignore_filenames.append(filename)
        self.additional_keys = additional_keys
        self.verbose = verbose
    
    def read_file(self, filename):
        if filename in self.ignore_filenames:
            return False
        else:
            return True
    
    def add(self, data):
        if not check_data_format(data, self.additional_keys):
            return False
        else:
            for key, values in self.ignore.items():
                if data[key] in values:
                    if self.verbose:
                        print('{} in the {} to ignore'.format(data[key], key))
                    return False
            return True


def get_data(manifest, data_dir, additional_keys, verbose=False):
    os.chdir(data_dir)
    # Initialise the filter
    data_filter = DataFilter(manifest, additional_keys, verbose)
    dataset = []
    for pathname in manifest['include']['pathnames']:
        # Sanity check
        if pathname in manifest['exclude'].get('pathnames', []):
            print('Error: {} both in exclude/include pathnames.'.format(pathname))
            print('Please double-check the manifest object.')
            exit()
        else:
            if verbose:
                print('Get {}'.format(pathname))
            for filename in glob.glob(pathname):
                if data_filter.read_file(filename):
                    with open (os.path.join(filename), 'rb') as fp:
                        data_file = json.load(fp)
                    for data in data_file:
                        if data_filter.add(data):
                            dataset.append(data)
                elif verbose:
                    print('Ignore this file : {}'.format(filename))
    return dataset
    
            
if __name__ == '__main__':
    data_dir = '/mnt/Documents/accurolab/toy_data_dir'
    additional_keys = []
    MANIFEST = {
        'include' : {
            'pathnames': [
                './CDC/articles*.json',
                './Wikipedia/articles*.json',
                './new_format/articles*.json'
            ]
        },
        'exclude': {
            'pathnames': [
                '.new_format/articles-learnaboutcovid-53-20201020-nf.json',
                './CKB/articles-jhk.json'
            ],
            'uri': [
                'https://learnaboutcovid19.org/article1',
                'https://www.uchicagomedicine.org/'
            ],
            'idSource': [
                'poynter',
                'ecdc'
            ],
            'id': [
                'f26313f3188a9ca6121d9de7e3cf8700b9808fb2bbc7aff011f7e091591a0563'
            ]
        } 
    }
    data = get_data(MANIFEST, data_dir, additional_keys, verbose=True)
    print(len(data))

