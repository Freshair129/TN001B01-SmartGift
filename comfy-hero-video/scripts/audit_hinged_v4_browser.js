(async () => {
  const videos = [...document.querySelectorAll('video')];
  const slider = document.querySelector('#scrub');
  if (videos.length !== 2 || videos.some(v => v.readyState < 2 || v.error)) {
    throw new Error('Both videos must be decoded before the audit');
  }
  const seek = async frame => {
    const waits = videos.map(video => new Promise(resolve => {
      if (Math.abs(video.currentTime-frame/30) < 0.0001 && !video.seeking) return resolve();
      video.addEventListener('seeked', resolve, {once:true});
    }));
    slider.value = String(frame);
    slider.dispatchEvent(new Event('input', {bubbles:true}));
    await Promise.all(waits);
    if (videos.some(v => Math.abs(v.currentTime-frame/30) > 0.001)) throw new Error('Seek mismatch');
    return {frame,times:videos.map(v=>v.currentTime)};
  };
  const reverse = [];
  for (const frame of [119,60,18,0]) reverse.push(await seek(frame));
  const pixels = videos.map(video => {
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth; canvas.height = video.videoHeight;
    const context = canvas.getContext('2d');
    context.drawImage(video,0,0);
    return context.getImageData(0,0,canvas.width,canvas.height).data;
  });
  let differentChannels = 0;
  for (let i=0;i<pixels[0].length;i++) if (pixels[0][i] !== pixels[1][i]) differentChannels++;
  if (differentChannels) throw new Error('Browser decoded closed frames differ');
  await videos[0].play();
  await new Promise(resolve=>setTimeout(resolve,350));
  const playbackAdvanced = videos[0].currentTime > 0;
  videos[0].pause();
  if (!playbackAdvanced) throw new Error('Native playback did not advance');
  await seek(0);
  return {status:'PASS',dimensions:videos.map(v=>[v.videoWidth,v.videoHeight]),
    durations:videos.map(v=>v.duration),reverse,closedFrameDifferentChannels:differentChannels,
    nativePlaybackAdvanced:playbackAdvanced,mediaErrors:videos.map(v=>v.error)};
})()
