from flask import Flask, request, render_template_string, jsonify
import requests
from bs4 import BeautifulSoup
import os
import openai
import time

# ---------- Config ----------

OPENAI_API_KEY = "YOUR API KEY HERE"   # <── just paste key inside quotes
openai.api_key = OPENAI_API_KEY

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 " \
             "(KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"

# ---------- Flask app ----------
app = Flask(__name__)

INDEX_HTML = '''
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Personal Web-connected AI Assistant</title>
  <style>
    body{font-family:Inter, system-ui, -apple-system, Arial; background:#f7f8fb;}
    .container{max-width:900px;margin:40px auto;background:#fff;padding:20px;border-radius:12px;box-shadow:0 6px 24px rgba(20,20,40,0.06)}
    textarea{width:100%;height:90px;padding:12px;border-radius:8px;border:1px solid #e6e9ef}
    button{background:#334155;color:#fff;padding:10px 14px;border-radius:8px;border:none}
    .row{display:flex;gap:8px;align-items:center}
    .result{white-space:pre-wrap;background:#0f172a;color:#fff;padding:12px;border-radius:8px;margin-top:12px}
    label{display:inline-flex;gap:8px;align-items:center}
  </style>
</head>
<body>
  <div class="container">
    <h2>Personal Web-connected AI Assistant</h2>
    <p>Type your question, choose format, and press Ask. The assistant will search the web and answer.</p>

    <form id="askForm">
      <textarea name="query" id="query" placeholder="Ask me anything.... "Explain CRISPR""></textarea>
      <div class="row" style="margin-top:8px">
        <label><input type="radio" name="mode" value="brief" checked> Brief</label>
        <label><input type="radio" name="mode" value="detailed"> Detailed</label>
        <label style="margin-left:auto">Max results: <select id="max_links" name="max_links"><option>2</option><option selected>3</option><option>5</option></select></label>
      </div>
      <div style="margin-top:12px">
        <button type="submit">Ask</button>
      </div>
    </form>

    <div id="answerArea"></div>
    <div id="metaArea" style="margin-top:12px;color:#475569"></div>
  </div>

<script>
const form = document.getElementById('askForm');
const answerArea = document.getElementById('answerArea');
const metaArea = document.getElementById('metaArea');
form.addEventListener('submit', async (e)=>{
  e.preventDefault();
  answerArea.innerHTML = 'Thinking...';
  metaArea.innerHTML = '';
  const data = new FormData(form);
  const body = { query: data.get('query'), mode: data.get('mode'), max_links: data.get('max_links') };
  const res = await fetch('/ask', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body)});
  const j = await res.json();
  if(j.error){ answerArea.innerHTML = '<div style="color:crimson">'+j.error+'</div>'; return; }
  answerArea.innerHTML = '<div class="result">'+j.answer+'</div>';
  metaArea.innerHTML = 'Sources: ' + j.sources.map(s=>`<a href="${s}" target="_blank">${s}</a>`).join(' | ');
});
</script>
</body>
</html>
'''


# ---------- Helper functions ----------

def google_search_links(query, num_results=3, pause=1.0):
   
    q = requests.utils.quote(query)
    url = f"https://www.google.com/search?q={q}&hl=en"
    headers = {"User-Agent": USER_AGENT}
    resp = requests.get(url, headers=headers, timeout=10)
    if resp.status_code != 200:
        raise RuntimeError(f"Google search failed with status {resp.status_code}")

    soup = BeautifulSoup(resp.text, 'html.parser')
    links = []
    
    for a in soup.find_all('a', href=True):
        href = a['href']
        if href.startswith('/url?q='):
            href = href.split('/url?q=')[1].split('&')[0]
            if href.startswith('http') and 'google' not in href:
                links.append(href)
        if len(links) >= num_results:
            break
    time.sleep(pause)
    return links


def fetch_page_text(url, timeout=8):
    headers = {"User-Agent": USER_AGENT}
    try:
        r = requests.get(url, headers=headers, timeout=timeout)
        if r.status_code != 200:
            return ''
        soup = BeautifulSoup(r.text, 'html.parser')
        
        for s in soup(['script','style','header','footer','nav','aside']):
            s.decompose()
        texts = [p.get_text(separator=' ', strip=True) for p in soup.find_all('p')]     
        texts = [t for t in texts if len(t) > 50]
        return '\n\n'.join(texts[:40])
    except Exception as e:
        return ''


def build_context_from_links(links):
    chunks = []
    for u in links:
        txt = fetch_page_text(u)
        if txt:
            chunks.append(f"URL: {u}\n\n{txt[:3000]}")
    return "\n\n----\n\n".join(chunks)


from openai import OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

def ask_openai_system(query, context, mode='brief'):
    if mode == 'brief':
        instruction = "Answer concisely in 3-5 sentences. If context is insufficient, state it but provide best-effort answer."
    else:
        instruction = "Give a detailed, structured answer. Use context and cite URLs if relevant."

    prompt = f"You are a helpful research assistant.\n\nQUESTION: {query}\n\nCONTEXT:\n{context}\n\n{instruction}"

    try:
        resp = client.chat.completions.create(
            model="gpt-4.1-mini",   
            messages=[
                {"role": "system", "content": "You answer using provided context and cite links when helpful."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=700,
            temperature=0.2
        )
        return resp.choices[0].message.content.strip()

    except Exception as e:
        raise RuntimeError(f"OpenAI request failed: {e}")


# ---------- Flask routes ----------
@app.route('/')
def index():
    return render_template_string(INDEX_HTML)


@app.route('/ask', methods=['POST'])
def ask_route():
    data = request.get_json() or {}
    query = data.get('query','').strip()
    mode = data.get('mode','brief')
    max_links = int(data.get('max_links',3))
    if not query:
        return jsonify({'error':'Empty query'})

    try:
        links = google_search_links(query, num_results=max_links)
    except Exception as e:
        return jsonify({'error':f'Search failed: {e}'})

    context = build_context_from_links(links)
    if not context:
        context = 'No page text could be extracted from the top results.'

    try:
        answer = ask_openai_system(query, context, mode=mode)
    except Exception as e:
        return jsonify({'error':str(e)})

    return jsonify({'answer': answer, 'sources': links})


if __name__ == '__main__':
   app.run(port=5050, debug=False, use_reloader=False) 
