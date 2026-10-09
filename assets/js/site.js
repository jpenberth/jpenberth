const t=document.querySelector('.top'),b=document.querySelector('.burger');
if(b)b.addEventListener('click',()=>{const o=t.classList.toggle('open');b.setAttribute('aria-expanded',o)});

// film grain: random gray noise on a small canvas, scaled up by CSS.
// data-interval = ms between new frames. data-fade (optional) = ms for a slow cross-fade between two stacked canvases,
// which turns Option B's grain into an almost-frozen frame that gently breathes into a new one.
(()=>{const cv=document.querySelector('canvas.tv');if(!cv)return;
const rm=matchMedia('(prefers-reduced-motion: reduce)');
const W=640,H=360,iv=+cv.dataset.interval||80,fade=+cv.dataset.fade||0;
function paint(c){c.width=W;c.height=H;const x=c.getContext('2d'),img=x.createImageData(W,H),d=img.data;
for(let i=0;i<d.length;i+=4){const v=Math.random()*255;d[i]=d[i+1]=d[i+2]=v;d[i+3]=255}x.putImageData(img,0,0)}
paint(cv);if(rm.matches)return;
if(!fade){let last=0;(function loop(t){if(!document.hidden&&t-last>iv){paint(cv);last=t}requestAnimationFrame(loop)})(0);return}
const target=parseFloat(getComputedStyle(cv.parentElement).getPropertyValue('--static'))||.3;
const b=cv.cloneNode(false);b.removeAttribute('data-interval');b.removeAttribute('data-fade');cv.after(b);
for(const c of [cv,b])c.style.transition='opacity '+fade+'ms linear';
cv.style.opacity=target;b.style.opacity=0;
let front=cv,back=b;
setInterval(()=>{if(document.hidden)return;paint(back);back.style.opacity=target;front.style.opacity=0;[front,back]=[back,front]},iv)})();
