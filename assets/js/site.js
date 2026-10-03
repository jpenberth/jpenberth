const t=document.querySelector('.top'),b=document.querySelector('.burger');
if(b)b.addEventListener('click',()=>{const o=t.classList.toggle('open');b.setAttribute('aria-expanded',o)});

// live TV static: random gray noise on a small canvas, redrawn ~12fps, scaled up by CSS
(()=>{const cv=document.querySelector('canvas.tv');if(!cv)return;
const rm=matchMedia('(prefers-reduced-motion: reduce)');
const W=640,H=360;cv.width=W;cv.height=H;const x=cv.getContext('2d'),img=x.createImageData(W,H),d=img.data;
function frame(){for(let i=0;i<d.length;i+=4){const v=Math.random()*255;d[i]=d[i+1]=d[i+2]=v;d[i+3]=255}x.putImageData(img,0,0)}
frame();if(rm.matches)return;
let last=0;(function loop(t){if(!document.hidden&&t-last>80){frame();last=t}requestAnimationFrame(loop)})(0)})();
