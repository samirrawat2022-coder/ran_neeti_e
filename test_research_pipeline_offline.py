import ast, pathlib, re, time
from unittest.mock import patch
import requests
here = pathlib.Path(__file__).resolve()
candidates = [here.parent / 'app.py', here.parent.parent / 'app.py']
candidates += [p / 'app.py' for p in here.parents]
candidates += list(here.parent.glob('*/app.py')) + list(here.parent.glob('*/*/app.py'))
app_path = next((p for p in candidates if p.is_file()), None)
if app_path is None:
    raise FileNotFoundError('Could not locate app.py. Checked: ' + ', '.join(str(p) for p in candidates))
src = app_path.read_text(encoding='utf-8')
tree=ast.parse(src)
names={'brave_web_search','format_research_context','call_gemini','build_prompt','retrieve_research'}
body=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name in names]
ns={'requests':requests,'re':re,'time':time,'brave_search_api_key':lambda:'fake-brave-key','gemini_model':lambda:'gemini-3.8-flash'}
exec(compile(ast.Module(body=body,type_ignores=[]),'<app-functions>','exec'),ns)

class SearchResp:
    status_code=200
    def raise_for_status(self): pass
    def json(self):
        return {'web':{'results':[{'title':'Team A beats Team B','url':'https://publisher.test/story','description':'Latest match report','extra_snippets':['Match statistics and context'],'page_age':'2026-11-17'}]}}
class GeminiResp:
    status_code=200
    def raise_for_status(self): pass
    def json(self): return {'candidates':[{'content':{'parts':[{'text':'RAN-NEETI analysis'}]}}]}

captured={}
def fake_get(url, **kwargs):
    captured['url']=url; captured['kwargs']=kwargs
    return SearchResp()
with patch.object(requests,'get',side_effect=fake_get):
    rows=ns['brave_web_search']('team A vs team B',limit=8)
assert len(rows)==1 and rows[0]['source']=='publisher.test' and rows[0]['url']=='https://publisher.test/story'
assert captured['url'].endswith('/v1/web/search')
assert captured['kwargs']['headers']['X-Subscription-Token']=='fake-brave-key'
ctx=ns['format_research_context'](rows)
assert '[1]' in ctx and 'publisher.test' in ctx and 'https://publisher.test/story' in ctx
prompt=ns['build_prompt']('SPORT','A vs B','none','Detailed','none',ctx)
assert 'RETRIEVED WEB SEARCH EVIDENCE' in prompt and 'Never copy Google/Brave search summaries' in prompt
captured_post={}
def fake_post(url, **kwargs):
    captured_post.update(kwargs); return GeminiResp()
with patch.object(requests,'post',side_effect=fake_post):
    answer,sources,model=ns['call_gemini']('test prompt','fake-key')
assert answer=='RAN-NEETI analysis' and model=='gemini-3.8-flash'
assert 'tools' not in captured_post['json']
print('PASS: Brave Search retrieval, evidence formatting, prompt construction, Gemini text-only payload')
