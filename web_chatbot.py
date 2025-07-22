from flask import Flask, request, jsonify, render_template_string
from chatbot import SQLDataQualityChatbot

app = Flask(__name__)
chatbot = SQLDataQualityChatbot()

HTML_PAGE = """
<!DOCTYPE html>
<html lang='en'>
<head>
    <meta charset='UTF-8'>
    <title>SQL Data Quality Chatbot</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f4f4f4; }
        #chatbox { width: 900px; min-height: 600px; margin: 40px auto; background: #fff; border-radius: 8px; box-shadow: 0 2px 8px #ccc; padding: 30px; }
        #messages { height: 500px; overflow-y: auto; border: 1px solid #eee; padding: 15px; margin-bottom: 15px; background: #fafafa; }
        .user { color: #0074D9; font-weight: bold; margin-bottom: 8px; }
        .assistant { color: #2ECC40; margin-bottom: 8px; }
        pre.sql { background: #272822; color: #f8f8f2; padding: 10px; border-radius: 6px; margin: 8px 0; font-size: 15px; overflow-x: auto; }
        code.sql { font-family: 'Fira Mono', 'Consolas', monospace; }
        #input { width: 85%; padding: 10px; font-size: 16px; }
        #send { padding: 10px 24px; font-size: 16px; }
    </style>
</head>
<body>
    <div id='chatbox'>
        <h2>SQL Data Quality Chatbot</h2>
        <div id='messages'></div>
        <input id='input' type='text' placeholder='Type your message...' autofocus />
        <button id='send'>Send</button>
    </div>
    <script>
        const messages = document.getElementById('messages');
        const input = document.getElementById('input');
        const send = document.getElementById('send');
        function appendMessage(role, text) {
            const div = document.createElement('div');
            div.className = role;
            if (role === 'assistant') {
                // Detect SQL code blocks and format them
                const sqlRegex = /```sql([\\s\\S]*?)```/g;
                let lastIndex = 0;
                let match;
                let html = '';
                while ((match = sqlRegex.exec(text)) !== null) {
                    // Add any text before the code block
                    if (match.index > lastIndex) {
                        let before = text.slice(lastIndex, match.index).trim();
                        if (before) {
                            // Format lists and paragraphs
                            before = before.replace(/\\n\\n+/g, '</p><p>');
                            before = before.replace(/(^|\\n)- (.*)/g, '<ul><li>$2</li></ul>');
                            html += '<div><p>' + before + '</p></div>';
                        }
                    }
                    // Add formatted SQL block
                    html += `<pre class='sql'><code class='sql'>${match[1].trim().replace(/</g, '&lt;').replace(/>/g, '&gt;')}</code></pre>`;
                    lastIndex = sqlRegex.lastIndex;
                }
                // Add any remaining text after last code block
                if (lastIndex < text.length) {
                    let after = text.slice(lastIndex).trim();
                    if (after) {
                        after = after.replace(/\\n\\n+/g, '</p><p>');
                        after = after.replace(/(^|\\n)- (.*)/g, '<ul><li>$2</li></ul>');
                        html += '<div><p>' + after + '</p></div>';
                    }
                }
                div.innerHTML = '<strong>Assistant:</strong><br>' + html;
            } else {
                div.innerHTML = '<strong>You:</strong> ' + text;
            }
            messages.appendChild(div);
            messages.scrollTop = messages.scrollHeight;
        }
        send.onclick = function() {
            const msg = input.value.trim();
            if (!msg) return;
            appendMessage('user', msg);
            input.value = '';
            fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: msg })
            })
            .then(res => res.json())
            .then(data => {
                appendMessage('assistant', data.response);
            });
        };
        input.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') send.click();
        });
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_PAGE)

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "")
    response = chatbot.send_message(user_input)
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(port=5000, debug=True)
