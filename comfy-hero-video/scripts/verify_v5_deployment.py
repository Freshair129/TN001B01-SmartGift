"""Read-only HTTP and browser checks against the existing local deployment."""
import hashlib
import json
import subprocess
import tempfile
import urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/v5'
NODE=Path(r'C:\Users\pc\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe')
BROWSER=Path(r'C:\Users\pc\AppData\Local\npm-cache\_npx\6de2aa2fded2970c\node_modules\agent-browser\bin\agent-browser.js')
http={}
for name in ['hero_west_receive.mp4','hero_east_discover.mp4','hero_frame0_poster.jpg']:
    url='http://localhost:8080/assets/videos/'+name+'?v=5'
    expected=(OUT/name).read_bytes()
    with urllib.request.urlopen(url) as response:
        data=response.read()
        assert response.status==200 and data==expected,name
    request=urllib.request.Request(url,headers={'Range':'bytes=0-99'})
    with urllib.request.urlopen(request) as response:
        assert response.status==206 and response.read()==expected[:100],name
        assert response.headers['Content-Range']==f'bytes 0-99/{len(expected)}'
    http[name]={'status':200,'range_status':206,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}
with urllib.request.urlopen('http://localhost:8080/?v=5') as response:
    cache=response.headers.get_all('Cache-Control')
    assert any('no-cache' in value and 'no-store' in value for value in cache),cache
    http['html_cache']=cache
(OUT/'deploy-http.json').write_text(json.dumps(http,indent=2))


def browser(*args,script=None):
    # A browser daemon can retain inherited output handles. A regular file avoids
    # waiting for pipe EOF after the short-lived CLI command has already exited.
    with tempfile.TemporaryFile(mode='w+',encoding='utf-8') as output:
        result=subprocess.run([str(NODE),str(BROWSER),'--session','smg-v5-final',*map(str,args)],
                              input=script,stdout=output,stderr=subprocess.STDOUT,
                              text=True,encoding='utf-8',timeout=45)
        output.seek(0)
        text=output.read()
    assert result.returncode==0,text
    return text


script=(ROOT/'scripts/audit_deployed_hero_v5.js').read_text(encoding='utf-8')
browser('open','http://localhost:8080/?v=5#archive')
for width,height in [(1920,1080),(1366,768),(390,844)]:
    browser('set','viewport',width,height)
    browser('open','http://localhost:8080/?v=5#archive')
    browser('wait','--load','networkidle')
    result=browser('eval','--stdin',script=script)
    assert 'PASS' in result,result
    (OUT/f'deploy-{width}.json').write_text(result,encoding='utf-8')
    # Capture the actual mouse-driven fully open state.
    browser('mouse','move',1,300)
    browser('wait',300)
    browser('screenshot',OUT/f'deploy-{width}.png')
    errors=browser('errors')
    (OUT/f'deploy-{width}-errors.txt').write_text(errors,encoding='utf-8')
    if errors.strip():print('BROWSER_ERROR_LOG',errors,flush=True)
    print('BROWSER_PASS',width,height,flush=True)
browser('close')
print('HTTP_AND_BROWSER_PASS',flush=True)
