const t=document.querySelector('.top'),b=document.querySelector('.burger');
if(b)b.addEventListener('click',()=>{const o=t.classList.toggle('open');b.setAttribute('aria-expanded',o)});

// live TV static: random gray noise on a small canvas, redrawn ~12fps, scaled up by CSS
(()=>{const cv=document.querySelector('canvas.tv');if(!cv)return;
const rm=matchMedia('(prefers-reduced-motion: reduce)');
const W=640,H=360;cv.width=W;cv.height=H;const x=cv.getContext('2d'),img=x.createImageData(W,H),d=img.data;
function frame(){for(let i=0;i<d.length;i+=4){const v=Math.random()*255;d[i]=d[i+1]=d[i+2]=v;d[i+3]=255}x.putImageData(img,0,0)}
frame();if(rm.matches)return;
let last=0;(function loop(t){if(!document.hidden&&t-last>80){frame();last=t}requestAnimationFrame(loop)})(0)})();

// contact form: posts to a Google Apps Script web app (rows land in a Google Sheet); falls back to the visitor's email app until an endpoint is set
(()=>{const f=document.getElementById('contact-form');if(!f)return;
const msg=f.querySelector('.fmsg'),btn=f.querySelector('button');
f.addEventListener('submit',async e=>{e.preventDefault();msg.className='fmsg';
const d=new FormData(f);const v=k=>String(d.get(k)||'').trim();
if(v('company'))return;                                   // spam trap
if(!v('name')||!v('message')||!/^\S+@\S+\.\S+$/.test(v('email'))){msg.className='fmsg err';msg.textContent='Please add your name, a valid email, and a message.';return}
const ep=f.dataset.endpoint;
if(!ep){location.href='mailto:'+f.dataset.email+'?subject='+encodeURIComponent((v('topic')||'Message')+' from '+v('name'))+'&body='+encodeURIComponent(v('message')+'\n\n'+v('name')+' <'+v('email')+'>');return}
btn.disabled=true;msg.textContent='Sending...';
try{
if(/formspree\.io/.test(ep)){                              // Formspree: JSON in, real success/error status out
d.set('_subject','jpenberth.com: '+(v('topic')||'New message')+' from '+v('name'));
const r=await fetch(ep,{method:'POST',headers:{'Accept':'application/json'},body:d});
if(!r.ok)throw new Error('formspree '+r.status)}
else{await fetch(ep,{method:'POST',mode:'no-cors',body:new URLSearchParams(d)})}   // Google Apps Script
f.reset();msg.className='fmsg ok';msg.textContent='Thank you. Your message is on its way.'}
catch(err){msg.className='fmsg err';msg.textContent='Something went wrong. Please email '+f.dataset.email+' directly.'}
finally{btn.disabled=false}})})();
