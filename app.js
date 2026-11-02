const filters=document.querySelectorAll('[data-filter]');
filters.forEach(button=>button.addEventListener('click',()=>{filters.forEach(b=>{b.classList.toggle('active',b===button);b.setAttribute('aria-pressed',String(b===button))});let count=0;document.querySelectorAll('.project').forEach(card=>{const visible=button.dataset.filter==='All'||card.dataset.category===button.dataset.filter;card.hidden=!visible;if(visible)count++});document.getElementById('project-count').textContent=`Showing ${count} project${count===1?'':'s'}`;}));
const cardVideo=document.querySelector('.card-video');
if(cardVideo && !window.matchMedia('(prefers-reduced-motion: reduce)').matches){
 let userPaused=false, automatic=false;
 cardVideo.addEventListener('pause',()=>{if(!automatic)userPaused=true});
 cardVideo.addEventListener('play',()=>{userPaused=false});
 new IntersectionObserver(entries=>{for(const entry of entries){if(entry.isIntersecting && !userPaused){cardVideo.play().catch(()=>{})}else if(!entry.isIntersecting && !cardVideo.paused){automatic=true;cardVideo.pause();setTimeout(()=>automatic=false,0)}}},{threshold:0.35}).observe(cardVideo);
}
