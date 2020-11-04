import os
import json

from utils import check_data_format
"""// Schema : manifest_object
// Purpose :
    Specifies file locations and documents to be included or excluded from
    the model. A file containing a single manifest_object is placed in
    the parent directory of the document store hierarchy.
{
  "include" : {
    "pathnames" : Array.of(String) // List of Unix path and filename
                                   // specifiers. Wild cards allowed.
   }
  "exclude" : {
    "pathnames" : Array.of(String) // List of Unix path and filename 
                                   // specifiers. Wild cards allowed.
    "id" : Array.of(String)        // id of document to exclude
    "uri" : Array.of(String)       // URI of document to exclude
    "idSource" : Array.of(String)  // Exclude all docs published by source
  }
}

    {
  // --[ mandatory ]---
  "title" : String,  // doc title in UTF-8
  "text" : String,   // doc body in UTF-8
  "uri" : String,    // permalink or a self-created URI
  "timestamp" : Number.min(0), // Unix timestamp in UTC at time of scrape
  "date" : String,   // timestamp, ISO 8601 format (eg: 2020-11-01T09:45:44Z)
  "id" : String,  // SHA-256 hash of "uri"+"timestamp"
  "idSource" : String, // Accurolab code name for the source

  // --[ optional ]--
  "html" : String,   // HTML of document body [null if unused] 
  "pubDate" : string  // publication date given by the source [null if unused] 

  // object containing source- and scraper-dependent 
  // additional metadata [null if unused]
  "extraMeta" : {
    "someItem" : String,  // [optional] exmaple item
    "anotherItem" : Number // [optional] exmaple item
  }
}


manifest = {
    'source_id_1' : 
    {
        'include': [list_of_paths or 'all' or 'none'],
        'exclude': [list_of_paths or 'all' or 'none']
    },
    'source_id_2': 
    {
        'include': [list_of_paths or 'all' or 'none'],
        'exclude': [list_of_paths or 'all' or 'none']
    }
}
"""


def get_data(manifest, data_dir, additional_keys, verbose=False):
    data = []
    for source_id, source_details in manifest.items():
        print(source_id)
        directory_path = os.path.join(data_dir, source_id)
        to_include = source_details['include']
        keep = 'some'
        if len(to_include) == 1:
            if to_include[0] == 'all':
                keep = 'all'
            elif to_include[0] == 'none':
                keep = 'none'
        to_exclude = source_details['exclude']
        exclude = 'some'
        if len(to_exclude) == 1:
            if to_exclude[0] == 'all':
                exclude = 'all'
            elif to_exclude[0] == 'none':
                exclude = 'none'
        keep_all, exclude_all = False, False
        if keep == 'all' and exclude == 'all':
            if verbose:
                print('Error in the manifest for {} - ignoring this source.'.format(source_id))
            continue
        elif keep == 'all':
            if exclude == 'none':
                keep_all = True
            else:
                # Include by default
                include_by_default =  True
                ids_to_include = {}
                for unique_id in to_exclude:
                    ids_to_include[unique_id] = False
        elif keep == 'none':
            if exclude == 'all':
                exclude_all = True
            else:
                include_by_default = False
                ids_to_include = {}
                for unique_id in to_include:
                    ids_to_include[unique_id] = True
        else:
            assert keep == 'some' and exclude == 'some'
            include_by_default = False ##Edge case, to discuss
            ids_to_include = {}
            for unique_id in to_include:
                ids_to_include[unique_id] = True
            for unique_id in to_exclude:
                ids_to_include[unique_id] = False

        if exclude_all:
            # Ignore this source
            continue
        
        for json_filename in os.listdir(directory_path):
            if json_filename.startswith('articles'):
                with open (os.path.join(directory_path, json_filename), 'rb') as fp:
                    articles = json.load(fp)
                for article in articles:
                    if not check_data_format(article, additional_keys):
                        continue
                    article_id = article.get('id')
                    if keep_all:
                        data.append(article)
                        if verbose:
                            print("append {}".format(article_id))
                    else:
                        include = ids_to_include.get(article_id, include_by_default)
                        if include:
                            data.append(article)
                            if verbose:
                                print("(+ {})".format(article_id))
                        elif verbose:
                            print("(\ {})".format(article_id))
    return data

    
            
if __name__ == '__main__':
    data_dir = '/mnt/Documents/accurolab/toy_data_dir'
    additional_keys = []
    MANIFEST = {
        'Wiki' : 
        {
            'include': ['all'],
            'exclude': ['none']
        },
        'CKB-articles-scrape': 
        {
            'include': ['none'],
            'exclude': ['all']
        },
        'CDC': 
        {
            'include': ['all'],
            'exclude': ['7bf27e80f51ccb80a74f9aec045caec603400472275c40bb6f5cea77',
                        '0af4e0df8d6619df920a181aacc80903e075fc1a88210d4290c7e918']
        }
    }
    data = get_data(MANIFEST, data_dir, additional_keys, verbose=True)


