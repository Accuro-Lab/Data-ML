// scrape-6.js
// Demo the use of Javascript Promises for building a web scraper.
// 2020-10-17 ITL
//
// Usage: node scrape-6.js
//
// Dependencies:
// npm install request request-promise jsdom @mozilla/readability
//
// Notes: the return value of callback passed to .then() becomes the
// resolved value of the promise object which .then() returns.
// See line 36.

const rp = require('request-promise');
const fs = require('fs'); // use the File System API
const { Readability } = require('@mozilla/readability');
const { JSDOM } = require('jsdom');

const testUrl = 'https://en.wikipedia.org/wiki/Wallaby'

function scrapeArticle(url){
  // return a promise object which will hold the result of an async page scrape
  // url = page to scrape
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
    });
  }

/* now scrape the page at testUrl
*/
scrapeArticle(testUrl).then(article =>{
  // print the value of the returned Promise when fulfilled
  console.log('article: ',article.title);
  console.log('byline: ',article.byline);
  console.log('length: ',article.length);
  console.log('excerpt: ',article.excerpt);
  console.log('siteName: ',article.siteName);
  })
  .catch(function(err){
    // trap errors here, at the _top_ of the promise chain
    console.log('Error caught: ' + err);
  })
  ;
