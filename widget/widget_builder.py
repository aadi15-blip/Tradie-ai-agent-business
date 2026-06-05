"""LocalFlow — Embeddable chat widget for existing websites.
Usage: <script src="https://yourdomain.com/widget.js" data-business-id="abc123"></script>
"""
import uuid, json

WIDGET_HTML = """
<div id="lf-chat-widget" style="
  position: fixed; bottom: 20px; right: 20px; z-index: 999999;
  font-family: 'Inter', -apple-system, sans-serif;
">
  <style>
    #lf-chat-widget * { box-sizing: border-box; margin: 0; padding: 0; }
    #lf-chat-bubble {
      width: 60px; height: 60px; border-radius: 50%;
      background: #2563eb; color: white; border: none;
      cursor: pointer; font-size: 28px; box-shadow: 0 4px 20px rgba(37,99,235,0.4);
      display: flex; align-items: center; justify-content: center;
      transition: transform 0.2s;
    }
    #lf-chat-bubble:hover { transform: scale(1.1); }
    #lf-chat-panel {
      position: fixed; bottom: 90px; right: 20px;
      width: 380px; height: 560px; max-height: 80vh;
      background: white; border-radius: 16px; box-shadow: 0 8px 40px rgba(0,0,0,0.15);
      display: none; flex-direction: column; overflow: hidden;
      border: 1px solid #e2e8f0;
    }
    #lf-chat-panel.open { display: flex; }
    #lf-chat-header {
      background: #2563eb; color: white; padding: 16px 20px;
      display: flex; align-items: center; gap: 10px;
    }
    #lf-chat-header h3 { font-size: 15px; font-weight: 600; }
    #lf-chat-header span { font-size: 12px; opacity: 0.8; }
    #lf-chat-close { margin-left: auto; background: none; border: none; color: white; cursor: pointer; font-size: 20px; }
    #lf-chat-messages { flex: 1; overflow-y: auto; padding: 16px; display: flex; flex-direction: column; gap: 8px; }
    .lf-msg { max-width: 80%; padding: 10px 14px; border-radius: 14px; font-size: 14px; line-height: 1.5; }
    .lf-msg.incoming { align-self: flex-start; background: #f1f5f9; border-bottom-left-radius: 4px; }
    .lf-msg.outgoing { align-self: flex-end; background: #2563eb; color: white; border-bottom-right-radius: 4px; }
    .lf-typing { align-self: flex-start; background: #f1f5f9; padding: 12px 16px; border-radius: 14px; }
    .lf-typing span { display: inline-block; width: 6px; height: 6px; background: #94a3b8; border-radius: 50%; margin: 0 2px; animation: lf-bounce 1.4s infinite both; }
    .lf-typing span:nth-child(2) { animation-delay: 0.2s; }
    .lf-typing span:nth-child(3) { animation-delay: 0.4s; }
    @keyframes lf-bounce { 0%,80%,100% { transform: scale(0); } 40% { transform: scale(1); } }
    #lf-chat-input { display: flex; padding: 12px 16px; border-top: 1px solid #e2e8f0; gap: 8px; }
    #lf-chat-input input { flex: 1; padding: 10px 14px; border: 1px solid #e2e8f0; border-radius: 10px; font-size: 14px; outline: none; }
    #lf-chat-input input:focus { border-color: #2563eb; }
    #lf-chat-input button { padding: 10px 16px; background: #2563eb; color: white; border: none; border-radius: 10px; cursor: pointer; font-weight: 600; font-size: 14px; }
    .lf-suggestions { display: flex; gap: 6px; padding: 8px 16px; flex-wrap: wrap; }
    .lf-suggestions button { padding: 6px 12px; background: #eff6ff; color: #2563eb; border: 1px solid #bfdbfe; border-radius: 16px; cursor: pointer; font-size: 12px; font-weight: 500; }
    .lf-suggestions button:hover { background: #dbeafe; }
    @media (max-width: 480px) {
      #lf-chat-panel { width: calc(100vw - 40px); right: 20px; bottom: 80px; height: 70vh; }
    }
  </style>
  <button id="lf-chat-bubble" onclick="toggleChat()">💬</button>
  <div id="lf-chat-panel">
    <div id="lf-chat-header">
      <div style="width:34px;height:34px;background:rgba(255,255,255,0.2);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:18px">🤖</div>
      <div><h3 id="lf-business-name">Chat with us</h3><span>🟢 Online — replies instantly</span></div>
      <button id="lf-chat-close" onclick="toggleChat()">✕</button>
    </div>
    <div id="lf-chat-messages"></div>
    <div id="lf-suggestions" class="lf-suggestions"></div>
    <div id="lf-chat-input">
      <input id="lf-msg-input" placeholder="Type a message..." onkeydown="if(event.key==='Enter')sendMsg()">
      <button onclick="sendMsg()">Send</button>
    </div>
  </div>
</div>
"""

SCRIPT_CODE = """
(function(){
  var bizId = %s;
  var apiUrl = %s;
  document.body.insertAdjacentHTML('beforeend', `%s`);
  var msgs = document.getElementById('lf-chat-messages');
  var inp = document.getElementById('lf-msg-input');
  var sug = document.getElementById('lf-suggestions');
  var nameEl = document.getElementById('lf-business-name');
  var sessionId = 'lf_' + Math.random().toString(36).slice(2,10);

  window.toggleChat = function(){
    var p = document.getElementById('lf-chat-panel');
    p.classList.toggle('open');
    if(p.classList.contains('open') && msgs.children.length === 0){
      addMsg('G\\'day! 👋 Need a hand? Just ask me about pricing, services, or book a visit!', 'incoming');
      showSuggestions();
    }
  };
  function addMsg(text, side){
    var d = document.createElement('div');
    d.className = 'lf-msg ' + side;
    d.textContent = text;
    msgs.appendChild(d);
    msgs.scrollTop = msgs.scrollHeight;
  }
  function showTyping(){ var d = document.createElement('div'); d.className = 'lf-typing'; d.id = 'lf-typing'; d.innerHTML = '<span></span><span></span><span></span>'; msgs.appendChild(d); msgs.scrollTop = msgs.scrollHeight; }
  function hideTyping(){ var t = document.getElementById('lf-typing'); if(t) t.remove(); }
  function showSuggestions(){
    sug.innerHTML = '';
    ['💰 How much for roof repairs?','📍 Do you work in my area?','📅 Book an inspection'].forEach(function(t){
      var b = document.createElement('button');
      b.textContent = t; b.onclick = function(){ inp.value = t; sendMsg(); };
      sug.appendChild(b);
    });
  }
  window.sendMsg = function(){
    var text = inp.value.trim();
    if(!text) return;
    addMsg(text, 'outgoing');
    inp.value = '';
    sug.innerHTML = '';
    showTyping();
    fetch(apiUrl + '/api/chat', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ message: text, session_id: sessionId }) })
      .then(function(r){ return r.json(); })
      .then(function(d){ hideTyping(); addMsg(d.response || 'No worries! Give us a call on 1300 273 976.', 'incoming'); showSuggestions(); })
      .catch(function(){ hideTyping(); addMsg('No worries! Give us a call on 1300 273 976 for a quick chat.', 'incoming'); showSuggestions(); });
  };
  // Auto-open after 4 seconds
  setTimeout(function(){ if(msgs.children.length === 0) window.toggleChat(); }, 4000);
  // Load business info
  if(bizId && bizId !== 'demo'){
    fetch(apiUrl + '/api/businesses/' + bizId).then(function(r){ return r.json(); }).then(function(b){ if(b && b.name) nameEl.textContent = b.name; }).catch(function(){});
  }
})();
"""

def generate_widget_script(business_id: str = "demo", api_url: str = "https://localflow-backend.up.railway.app") -> str:
    """Generate the complete widget script for a business."""
    return f"""<script>
(function(){{
  var bizId = '{business_id}';
  var apiUrl = '{api_url}';
  document.body.insertAdjacentHTML('beforeend', `{WIDGET_HTML}`);
  var msgs = document.getElementById('lf-chat-messages');
  var inp = document.getElementById('lf-msg-input');
  var sug = document.getElementById('lf-suggestions');
  var nameEl = document.getElementById('lf-business-name');
  var sessionId = 'lf_' + Math.random().toString(36).slice(2,10);

  window.toggleChat = function(){{
    var p = document.getElementById('lf-chat-panel');
    p.classList.toggle('open');
    if(p.classList.contains('open') && msgs.children.length === 0){{
      addMsg("G'day! 👋 Need a hand? Just ask me about pricing, services, or book a visit!", 'incoming');
      showSuggestions();
    }}
  }};
  function addMsg(text, side){{
    var d = document.createElement('div');
    d.className = 'lf-msg ' + side;
    d.textContent = text;
    msgs.appendChild(d);
    msgs.scrollTop = msgs.scrollHeight;
  }}
  function showTyping(){{ var d = document.createElement('div'); d.className = 'lf-typing'; d.id = 'lf-typing'; d.innerHTML = '<span></span><span></span><span></span>'; msgs.appendChild(d); msgs.scrollTop = msgs.scrollHeight; }}
  function hideTyping(){{ var t = document.getElementById('lf-typing'); if(t) t.remove(); }}
  function showSuggestions(){{
    sug.innerHTML = '';
    ['💰 How much for roof repairs?','📍 Do you work in my area?','📅 Book an inspection'].forEach(function(t){{
      var b = document.createElement('button');
      b.textContent = t; b.onclick = function(){{ inp.value = t; sendMsg(); }};
      sug.appendChild(b);
    }});
  }}
  window.sendMsg = function(){{
    var text = inp.value.trim();
    if(!text) return;
    addMsg(text, 'outgoing');
    inp.value = '';
    sug.innerHTML = '';
    showTyping();
    fetch(apiUrl + '/api/chat', {{ method:'POST', headers:{{'Content-Type':'application/json'}}, body: JSON.stringify({{ message: text, session_id: sessionId }}) }})
      .then(function(r){{ return r.json(); }})
      .then(function(d){{ hideTyping(); addMsg(d.response || "No worries! Give us a call.", 'incoming'); showSuggestions(); }})
      .catch(function(){{ hideTyping(); addMsg("No worries! Give us a call for a quick chat.", 'incoming'); showSuggestions(); }});
  }};
  setTimeout(function(){{ if(msgs.children.length === 0) window.toggleChat(); }}, 4000);
  if(bizId && bizId !== 'demo'){{
    fetch(apiUrl + '/api/businesses/' + bizId).then(function(r){{ return r.json(); }}).then(function(b){{ if(b && b.name) nameEl.textContent = b.name; }}).catch(function(){{}});
  }}
}})();
</script>"""/home/engine/.bashrc: line 1: syntax error near unexpected token `('
/home/engine/.bashrc: line 1: `. /etc/profile.d/workload-containment.shn# ~/.bashrc: executed by bash(1) for non-login shells.'
/home/engine/.bashrc: line 1: syntax error near unexpected token `('
/home/engine/.bashrc: line 1: `. /etc/profile.d/workload-containment.shn# ~/.bashrc: executed by bash(1) for non-login shells.'
/home/engine/.bashrc: line 1: syntax error near unexpected token `('
/home/engine/.bashrc: line 1: `. /etc/profile.d/workload-containment.shn# ~/.bashrc: executed by bash(1) for non-login shells.'
