liked = document.getElementById("liked");
likeCheckbox = document.getElementById("checkbox");
alertBox = document.getElementById("alert-box");
let timeOut = null;
const queryString = window.location.search;
const urlParams = new URLSearchParams(queryString);
const filterBtn = document.getElementById('navbarDropdownMenuLinkFilter');
const sortBtn = document.getElementById('navbarDropdownMenuLinkSort');
const filterArea = document.getElementById('filterArea');
const sortArea = document.getElementById('sortArea');
const searchArea = document.getElementById('q');
const searchForm = document.getElementById('qform');


try{ 
    if(urlParams.has('q')){
        document.getElementById('q').value = urlParams.get('q')
    }
    if(urlParams.has('category') && urlParams.get('category')!='Toate'){
        filterBtn.classList.replace('text-dark', 'text-primary')
        filterBtn.innerHTML = '<i class="bi bi-funnel-fill"></i>'
    }
    if(urlParams.has('order')){
        sortBtn.classList.replace('text-dark', 'text-primary')
    }
}catch(err){}

if(filterArea){
    filterArea.addEventListener('click',(e)=>{
        let newUrl = new URL(window.location);
        newUrl.searchParams.set('category',String(e.target.textContent))
        newUrl.searchParams.set('page','1')
        window.location.href = newUrl;
    })
}

if(sortArea){
    sortArea.addEventListener('click',(e)=>{
        let newUrl = new URL(window.location);
        newUrl.searchParams.set('order',String(e.target.textContent))
        newUrl.searchParams.set('page','1')
        window.location.href = newUrl;
    })
}

function alertMsg(color,message){

    clearTimeout(timeOut);
    alertHtml = `<div class="alert alert-${color}" role="alert">
                   ${message}
                </div>`;
    alertBox.scrollIntoView();
    alertBox.innerHTML = alertHtml;
    let secs = 3;
    x = setInterval(()=>{
        alertBox.innerHTML = `<div class="alert alert-${color}" role="alert">
                            ${message} Redirectionare in (${secs})</div>`
        secs -= 1;
    },1000)
    timeOut = setTimeout(()=>{
        clearInterval(x);
        alertBox.innerHTML = "";
        window.location.href = `/accounts/login/?next=${window.location.pathname}`;
    },4000)
    
}

function commentAlert(){
    alertMsg('danger','Trebuie sa fii autentificat(a) pentru a putea posta un comentariu!');
    
}

const cookieContainer = document.querySelector("#cookie-container");
const cookieButton = document.querySelector("#cookie-btn");
const hasCookieUse = document.cookie
    .split('; ')
    .find(row => row.startsWith('cookieUse='));

cookieButton.addEventListener("click", () => {
    cookieContainer.classList.remove("active");
    let date = new Date();
    date.setMonth(date.getMonth() + 6);
    date = date.toUTCString();
    document.cookie = "cookieUse=1; path=/; expires=" + date;
});


setTimeout(() => {
  if (!hasCookieUse) {
    cookieContainer.classList.add("active");
  }
}, 2000);


jQuery("#flexSwitch").change(function(){
    jQuery("#email-notif-acc").submit();
});


mediumZoom(document.querySelector('#zoom-img'), {
    scrollOffset: 0,
    background: 'rgba(25, 18, 25, .9)',
})

mediumZoom(document.querySelectorAll('.zoom-imgs'), {
    scrollOffset: 0,
    background: 'rgba(25, 18, 25, .9)',
})