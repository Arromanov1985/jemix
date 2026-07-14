function findAPI(win){var n=0;while(win&&n<500){if(win.API)return win.API;n++;if(win.parent===win)break;win=win.parent;}return null;}
var API=findAPI(window)||(window.opener?findAPI(window.opener):null);var scormReady=false;
function scormInit(){if(!API)return false;try{scormReady=API.LMSInitialize("")==="true";if(scormReady){API.LMSSetValue("cmi.core.lesson_status","incomplete");API.LMSCommit("");}return scormReady;}catch(e){return false;}}
function scormSet(score,status){if(!API||!scormReady)return;try{API.LMSSetValue("cmi.core.score.raw",String(score));API.LMSSetValue("cmi.core.lesson_status",status);API.LMSCommit("");}catch(e){}}
function scormFinish(){if(!API||!scormReady)return;try{API.LMSCommit("");API.LMSFinish("");}catch(e){}}
window.addEventListener("load",scormInit);window.addEventListener("beforeunload",scormFinish);
