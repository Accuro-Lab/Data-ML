#!/usr/bin/env bash
#
# scrape-articles.bash
# Demo to scrape articles from a list of urls in the file: urls.txt
# ITL 2020-10-17
#
# Usage:
# chmod +x scrape-articles.bash
# ./scrape-articles.bash
#
# Outputs one JSON file and one HTML file for each url scraped.
# The filenames are prefix with 'outfile-' followed by a timestamp.
#
# Dependencies:
# scrape-4.js
# urls.txt  ## text file containing one url per line
#
while read line; do
  eval $(
    echo $line |
    sed -E "s/.*/node scrape-4.js & outfile-`date +\"%Y-%m-%d-%H-%M-%S\"`/"
  )
done < urls.txt
