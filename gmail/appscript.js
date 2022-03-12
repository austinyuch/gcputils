
const arrQuery = [
  ["from:raymondwang174@gmail.com",
        "is:unread",
        "newer_than:3d"
       ]
]

function batchDeleteEmail(strQuery) {
  var batchSize = 100 // Process up to 100 threads at once
  var searchSize = 400 // Limit search result to a max of 400 threads. Use this if you encounter the "Exceeded maximum execution time" error
  
  // var threads = GmailApp.search('label:inbox from:user@example.com', 0, searchSize);
  var threads = GmailApp.search(strQuery, 0, searchSize);
  for (j = 0; j < threads.length; j+=batchSize) {
    GmailApp.moveThreadsToTrash(threads.slice(j, j+batchSize));
  }
}

function batchSearchAndbatchDeleteEmail() {
  array.forEach(function (item, index) {
    // console.log(arrItem, index);
    let str_query = arrItem.join(" ");
    batchDeleteEmail(str_query);
  });
}

batchSearchAndbatchDeleteEmail();