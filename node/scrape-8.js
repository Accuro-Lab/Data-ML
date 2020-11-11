// scrape-8.js
// Demonstrate the use of Javascript Promises for building a web scraper.
// Scrape multiple pages and wait for completion using Promise.allSettled()
// 2020-10-18 ITL
//
// Usage: node scrape-8.js input_file output_file
//
// where input_file contains a list of URLs to scrape
// and output_file will contain a JSON array with the scraped articles
//
// Dependencies:
// npm install request request-promise jsdom \
//        @mozilla/readability readline-promise
//
// Notes: the return value of callback passed to .then() becomes the
// resolved value of the promise object which .then() returns.

const rp = require('request-promise');
const fs = require('fs'); // use the File System API
const { Readability } = require('@mozilla/readability');
const { JSDOM } = require('jsdom');
const readline = require('readline-promise').default;

const scrapedArticles = [];
const scrapeResults = []; // result array

const infile = process.argv[2]; // input filename
const outfile = process.argv[3]; //  output filename

function scrapeArticle(url){
  // return a promise object which will hold the result of an async page scrape
  return (new rp(url))
    .then(function(html){

      // parse the scraped html using readability
      let doc = new JSDOM(html,url); // create a DOM object
      let reader = new Readability(doc.window.document);
      let article = reader.parse();

      // insert additional metadata
      article.url = url;
      article.scrapeDate = (new Date()).toISOString();
      article.scrapeTimestamp = Date.now();

      return article; // becomes the resolved value of the returned promise
    })
    .catch(function(err){
      console.log('Error caught in scrapeArticle: ' + err);
    });
  }

/* Read URLs from file and initiate web scrapes by adding promises
** to the result array
*/
async function loadUrls(){
  console.log('loadUrls: Reading URLs from file ...');

  var rlp = readline.createInterface(
    { input: fs.createReadStream(infile) }
    );
    
  console.log('loadUrls: Initiating scrapes ...');
  for await (const line of rlp) {
      console.log(line);
      scrapeResults.push( scrapeArticle(line) );
    };

}


/*  Wait for promise fulfillment
*/
async function getResults(){
  console.log('getResults: Waiting for scrapes to complete ...');
  await Promise.allSettled(scrapeResults)
    .then(results => {
      console.log('getResults: All scrapes done');
      console.log('scrapeResults.length: ', scrapeResults.length)

      results.forEach((results) => {
        // populate the results array
        console.log(results.value.title);
        scrapedArticles.push( results.value );
        });
      })
    .catch(function(err){
      console.log('getResults: Error caught: ' + err);
    });
}

async function main(){
  console.log('** BEGIN **');
  console.log('infile: ',infile);
  console.log('outfile: ',outfile);
  await loadUrls();
  await getResults();
  console.log('Writing to output file ...');
  console.log('scrapedArticles.length: ', scrapedArticles.length);
  fs.writeFileSync(outfile, JSON.stringify(scrapedArticles,null,2));
}

main();
