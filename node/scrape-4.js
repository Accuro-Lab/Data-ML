// scrape-4.js
// Demo of Mozilla Readability module as the basis of a web page scraper.
// 2020-10-17 ITL
//
// Usage: node scrape-4.js https://desired.webpage.com basefilename
//
// Example: node scrape-4.js https://en.wikipedia.org/wiki/Wallaby outfile
//
// Scrape a web page and use Readability to extract the article text.
// Take the URL and the output file name from command line arguments.
// Outputs two files: basefilename.JSON and basefilename.HTML
//
// Note: all the processing has to be done in the callback function,
// otherwise the script ends before the http request has returned.
//
// Dependencies:
// npm install request request-promise jsdom @mozilla/readability
//
// History:
// 2020-10-28 Updated to output a JSON _array_ containing one object.
//            Maintains compatibility with other scraping script outputs.
//

const rp = require('request-promise');
const fs = require('fs'); // use the File System API
const { Readability } = require('@mozilla/readability');
const { JSDOM } = require('jsdom');

const resultArray = [];

// Read command line arguments
var url = process.argv[2];
var outfile = process.argv[3];

// Get the web page using the resquest-promise API.
// This is an async call which returns a Javascript Promise.
rp(url)
  .then(function(html){
    // parse the scraped html using readability
    let doc = new JSDOM(html,url); // create a DOM object
    let reader = new Readability(doc.window.document);
    let article = reader.parse();

    // insert additional metadata
    article.url = url;
    article.scrapeDate = (new Date()).toISOString();
    article.scrapeTimestamp = Date.now();

    resultArray.push(article);  // output a JSON array containing one object

    // synchronous write to output files
    fs.writeFileSync(outfile+'.json', JSON.stringify(resultArray,null,2));
    fs.writeFileSync(outfile+'.html', article.content);

    // print extracted metadata to console
    console.log('title: ',article.title);
    console.log('byline: ',article.byline);
    console.log('dir: ',article.dir);
    console.log('length: ',article.length);
    console.log('excerpt: ',article.excerpt);
    console.log('siteName: ',article.siteName);
    console.log('url: ',article.url);
    console.log('scrapeDate: ',article.scrapeDate);
    console.log('scrapeTimestamp: ',article.scrapeTimestamp);
    /*
    console.log('content: ',article.content);  // HTML of article body
    console.log('textContent: ',article.textContent); // plain text
    */
    })
  .catch(function(err){
    console.log('Error caught: ' + err);
    });
