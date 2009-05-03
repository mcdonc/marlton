function feed_insert(element,result) {
var msg = document.getElementById(element);
for (var i = 0; i < result.feed.entries.length; i++) {
  var entry = result.feed.entries[i];
  var link = '<a href="' + entry.link + '">' + entry.title + '</a>';
  msg.innerHTML = msg.innerHTML + '<li>' + link + '</li>';
};
}

