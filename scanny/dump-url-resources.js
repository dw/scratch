var system = require('system');
var webpage = require('webpage');

function log()
{
    var array = Array.prototype.slice.call(arguments);
    console.log(JSON.stringify(array));
}

var page = webpage.create();
page.onUrlChanged = function(url) { log('url', url); };
page.onResourceRequested = function(req) { log('request', req); };
page.onResourceReceived = function(resp) { log('response', resp); };
page.onError = function(msg, trace) { log('js-error', msg); };
page.onResourceError = function(error) { log('error', error); };
page.onLoadFinished = function(status) {
    log('done', status);
    phantom.exit();
};

page.open(system.args[1]);
