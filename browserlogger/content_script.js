// A content script is “a JavaScript file that runs in the context of web pages.” This means that a content script can interact with web pages that the browser visits.
// https://developer.chrome.com/extensions/content_scripts


// https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/oncopy
// document.body.oncopy = document.body.oncut = (event) => {
//     console.log("copy");
//     console.log(event);
// };

// https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/onpaste
document.body.onpaste = (e) => {
    console.log("paste");
    let eventLog = { 
        timestamp: new Date(Date.now()).toISOString().replace('T',' ').slice(0, -1),
        category: "Browser",
        application: getBrowser(),
        event_type: "paste",
        clipboard_content: e.clipboardData.getData('text/plain'),
        browser_url: document.URL
    };
    console.log(JSON.stringify(eventLog));
    post(eventLog);
};

// // https://developer.mozilla.org/en-US/docs/Web/API/GlobalEventHandlers/onclick
// document.body.onclick = (e) => {
//     console.log("paste");
//     let eventLog = { 
//         timestamp: new Date(Date.now()).toISOString().replace('T',' ').slice(0, -1),
//         category: "Browser",
//         application: getBrowser(),
//         event_type: "paste",
//         clipboard_content: e.clipboardData.getData('text/plain'),
//         browser_url: document.URL
//     };
//     console.log(JSON.stringify(eventLog));
//     post(eventLog);
// };

// // https://developer.mozilla.org/en-US/docs/Web/API/GlobalEventHandlers/onchange
// document.body.onchange = (e) => {
//     console.log("paste");
//     let eventLog = { 
//         timestamp: new Date(Date.now()).toISOString().replace('T',' ').slice(0, -1),
//         category: "Browser",
//         application: getBrowser(),
//         event_type: "paste",
//         clipboard_content: e.clipboardData.getData('text/plain'),
//         browser_url: document.URL
//     };
//     console.log(JSON.stringify(eventLog));
//     post(eventLog);
// };

// //
// document.body.onkeypress = (e) => {
//     console.log("paste");
//     let eventLog = { 
//         timestamp: new Date(Date.now()).toISOString().replace('T',' ').slice(0, -1),
//         category: "Browser",
//         application: getBrowser(),
//         event_type: "paste",
//         clipboard_content: e.clipboardData.getData('text/plain'),
//         browser_url: document.URL
//     };
//     console.log(JSON.stringify(eventLog));
//     post(eventLog);
// };


function post(eventLog) {
    // var storage = (localStorage.getItem('checkboxValue') || {}) == 'true';
    // if (storage === true) {
    // console.log("Recording Enabled")
    
    $.ajax({
        type: "POST",
        url: "http://127.0.0.1:4444/",
        crossDomain: true,
        contentType: 'application/json',
        data: JSON.stringify(eventLog),
        success: function (responseData, status, xhr) {
            console.log("Request Successful!" + responseData);
        },
        error: function (request, status, error) {
            console.log("Request Failed! " + JSON.stringify(request) + 'Status ' + status + "Error msg: " + error);
        }
    });
    
    // } else {
    //     console.log("Recording Disabled");
    // }
}

function getBrowser() {
    if (typeof chrome !== "undefined") {
        if (typeof browser !== "undefined") 
        return "Firefox";
        else 
        return "Chrome";
    }
}

