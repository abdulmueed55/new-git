/* Runs before paint so the saved theme never flashes. Keep this inline-small. */
(function(){try{var t=localStorage.getItem('ff-theme');if(t==='dark'||t==='light'){document.documentElement.setAttribute('data-theme',t);}}catch(e){}})();
