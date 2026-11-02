const studyLinks=[...document.querySelectorAll('.study-nav a')];
const studySections=studyLinks.map(a=>document.querySelector(a.getAttribute('href'))).filter(Boolean);
if(studySections.length){
 const visibleSections=new Map();
 const updateCurrent=()=>{const candidates=studySections.filter(s=>visibleSections.get(s.id));if(!candidates.length)return;const active=candidates[0].id;studyLinks.forEach(a=>{const selected=a.getAttribute('href')==='#'+active;a.classList.toggle('current',selected);if(selected)a.setAttribute('aria-current','location');else a.removeAttribute('aria-current')})};
 const observer=new IntersectionObserver(entries=>{entries.forEach(e=>visibleSections.set(e.target.id,e.isIntersecting));updateCurrent()},{rootMargin:'-150px 0px -30% 0px',threshold:0});
 studySections.forEach(s=>observer.observe(s));
}

// A local, accessible image viewer for project figures.
(()=>{
 const links=[...document.querySelectorAll('.technical-figure>a')].filter(a=>a.querySelector('img')&&/\.(svg|png|jpe?g|webp)(?:[?#]|$)/i.test(a.href));
 if(!links.length||!window.HTMLDialogElement)return;
 const dialog=document.createElement('dialog');dialog.className='figure-viewer';dialog.setAttribute('aria-label','Figure viewer');
 dialog.innerHTML='<div class="figure-viewer-toolbar"><span class="figure-viewer-title"></span><div class="figure-viewer-actions"><button type="button" data-action="out" aria-label="Zoom out">−</button><output aria-live="polite" aria-label="Zoom level">100%</output><button type="button" data-action="in" aria-label="Zoom in">+</button><button type="button" data-action="reset">Reset</button><a class="figure-viewer-original" target="_blank" rel="noopener">Open original</a><button type="button" data-action="close" aria-label="Close figure viewer">Close ×</button></div></div><div class="figure-viewer-stage" tabindex="0" aria-label="Figure. Scroll or pinch to zoom, and drag to pan."><img draggable="false" alt=""></div><p class="figure-viewer-help">Scroll or pinch to zoom · Drag to pan · + / − to zoom · 0 to reset · Esc to close</p>';
 document.body.append(dialog);
 const stage=dialog.querySelector('.figure-viewer-stage'),img=stage.querySelector('img'),output=dialog.querySelector('output'),title=dialog.querySelector('.figure-viewer-title'),original=dialog.querySelector('.figure-viewer-original');
 let zoom=1,base=1,x=0,y=0,oldOverflow='',opener=null;
 const pointers=new Map();let previousDistance=0;
 function render(){img.style.transform=`translate(-50%,-50%) translate(${x}px,${y}px) scale(${base*zoom})`;output.textContent=Math.round(zoom*100)+'%';stage.classList.toggle('is-zoomed',zoom>1.01);}
 function fit(){base=Math.min(stage.clientWidth*.94/(img.naturalWidth||1200),stage.clientHeight*.94/(img.naturalHeight||700));img.style.width=(img.naturalWidth||1200)+'px';img.style.height=(img.naturalHeight||700)+'px';render();}
 function reset(){zoom=1;x=0;y=0;fit();}
 function setZoom(next,px=0,py=0){const value=Math.min(12,Math.max(.5,next)),ratio=value/zoom;x=px-(px-x)*ratio;y=py-(py-y)*ratio;zoom=value;render();}
 function location(e){const r=stage.getBoundingClientRect();return {x:e.clientX-r.left-r.width/2,y:e.clientY-r.top-r.height/2};}
 function open(a){opener=a;oldOverflow=document.body.style.overflow;document.body.style.overflow='hidden';title.textContent=a.closest('figure').querySelector('figcaption strong')?.textContent||a.querySelector('img').alt||'Figure';img.alt=a.querySelector('img').alt;original.href=a.href;zoom=1;x=0;y=0;dialog.showModal();img.onload=reset;img.src=a.href;stage.focus();}
 links.forEach(a=>{a.setAttribute('aria-haspopup','dialog');a.setAttribute('aria-label','Zoom image: '+a.querySelector('img').alt);a.addEventListener('click',e=>{if(e.button!==0||e.metaKey||e.ctrlKey||e.shiftKey||e.altKey)return;e.preventDefault();open(a);});const badge=a.querySelector('.figure-zoom');if(badge)badge.textContent='+';});
 dialog.addEventListener('close',()=>{document.body.style.overflow=oldOverflow;pointers.clear();previousDistance=0;opener?.focus();});
 dialog.querySelectorAll('button').forEach(button=>button.addEventListener('click',()=>{const action=button.dataset.action;if(action==='close')dialog.close();else if(action==='reset')reset();else setZoom(zoom*(action==='in'?1.4:1/1.4));}));
 dialog.addEventListener('keydown',e=>{if(['+','=','-','0'].includes(e.key)){e.preventDefault();if(e.key==='0')reset();else setZoom(zoom*(e.key==='-'?1/1.25:1.25));}});
 stage.addEventListener('wheel',e=>{e.preventDefault();const p=location(e);setZoom(zoom*Math.exp(-e.deltaY*.0015),p.x,p.y);},{passive:false});
 stage.addEventListener('dblclick',e=>{const p=location(e);if(zoom>1.1)reset();else setZoom(2.5,p.x,p.y);});
 stage.addEventListener('pointerdown',e=>{if(e.button!==0)return;e.preventDefault();stage.setPointerCapture(e.pointerId);pointers.set(e.pointerId,location(e));if(pointers.size===2){const [a,b]=[...pointers.values()];previousDistance=Math.hypot(a.x-b.x,a.y-b.y);}stage.classList.add('is-dragging');});
 stage.addEventListener('pointermove',e=>{if(!pointers.has(e.pointerId))return;const prev=pointers.get(e.pointerId),p=location(e);pointers.set(e.pointerId,p);if(pointers.size===2){const [a,b]=[...pointers.values()],distance=Math.hypot(a.x-b.x,a.y-b.y);if(previousDistance>0)setZoom(zoom*distance/previousDistance,(a.x+b.x)/2,(a.y+b.y)/2);previousDistance=distance;}else if(pointers.size===1){x+=p.x-prev.x;y+=p.y-prev.y;render();}});
 function release(e){pointers.delete(e.pointerId);previousDistance=0;if(!pointers.size)stage.classList.remove('is-dragging');}
 ['pointerup','pointercancel','lostpointercapture'].forEach(type=>stage.addEventListener(type,release));
 window.addEventListener('resize',()=>{if(dialog.open)fit();});
})();
