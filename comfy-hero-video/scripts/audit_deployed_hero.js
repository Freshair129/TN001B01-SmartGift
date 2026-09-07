(async()=>{
  const videos=[...document.querySelectorAll('#main-canvas video')];
  const sleep=t=>new Promise(r=>setTimeout(r,t));
  if(videos.length!==2 || videos.some(v=>v.readyState<2 || v.duration!==4 || !v.currentSrc.endsWith('?v=4'))) throw new Error('Wrong or unready deployed media');
  const state=()=>videos.map(v=>({time:v.currentTime,shown:getComputedStyle(v).display!=='none',src:v.currentSrc}));
  dispatchEvent(new MouseEvent('mousemove',{clientX:1,clientY:300}));await sleep(250);const left=state();
  if(left[1].time<3.9 || !left[1].shown) throw new Error('Mouse-left mapping failed');
  dispatchEvent(new MouseEvent('mousemove',{clientX:innerWidth-1,clientY:300}));await sleep(250);const right=state();
  if(right[0].time<3.9 || !right[0].shown) throw new Error('Mouse-right mapping failed');
  dispatchEvent(new MouseEvent('mousemove',{clientX:innerWidth/2,clientY:300}));await sleep(250);const center=state();
  if(center.some(v=>v.time!==0)) throw new Error('Center must reset both clips');
  const pixels=videos.map(v=>{let c=document.createElement('canvas');c.width=1920;c.height=1080;let x=c.getContext('2d');x.drawImage(v,0,0);return x.getImageData(0,0,1920,1080).data});
  let differences=0;for(let i=0;i<pixels[0].length;i++)if(pixels[0][i]!==pixels[1][i])differences++;
  if(differences)throw new Error('Browser closed frame mismatch');
  const rect=videos[0].getBoundingClientRect(),scale=Math.min(rect.width/1920,rect.height/1080);
  const x=rect.left+(rect.width-1920*scale)/2,y=rect.top+(rect.height-1080*scale)/2;
  const bounds={left:x+431.2688*scale,top:y+93.9492*scale,right:x+1488.7312*scale,bottom:y+1020.4412*scale};
  const overlap=r=>bounds.left<r.right&&bounds.right>r.left&&bounds.top<r.bottom&&bounds.bottom>r.top;
  const ledger=document.querySelector('#outro-info').getBoundingClientRect();
  const logo=document.querySelector('.logo').getBoundingClientRect();
  if(overlap(ledger)||overlap(logo))throw new Error('Hero overlaps fixed copy');
  return {status:'PASS',viewport:[innerWidth,innerHeight],left,right,center,closedDifferentChannels:differences,
    bounds,ledgerOverlap:false,logoOverlap:false,videoFit:getComputedStyle(videos[0]).objectFit,mediaErrors:videos.map(v=>v.error)};
})()
