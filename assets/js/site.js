const t=document.querySelector('.top'),b=document.querySelector('.burger');
if(b)b.addEventListener('click',()=>{const o=t.classList.toggle('open');b.setAttribute('aria-expanded',o)});
