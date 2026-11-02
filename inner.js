const studyLinks=[...document.querySelectorAll('.study-nav a')];
const studySections=studyLinks.map(a=>document.querySelector(a.getAttribute('href'))).filter(Boolean);
if(studySections.length){
 const visibleSections=new Map();
 const updateCurrent=()=>{const candidates=studySections.filter(s=>visibleSections.get(s.id));if(!candidates.length)return;const active=candidates[0].id;studyLinks.forEach(a=>{const selected=a.getAttribute('href')==='#'+active;a.classList.toggle('current',selected);if(selected)a.setAttribute('aria-current','location');else a.removeAttribute('aria-current')})};
 const observer=new IntersectionObserver(entries=>{entries.forEach(e=>visibleSections.set(e.target.id,e.isIntersecting));updateCurrent()},{rootMargin:'-150px 0px -30% 0px',threshold:0});
 studySections.forEach(s=>observer.observe(s));
}
