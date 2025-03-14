from flask import Flask, render_template_string

app = Flask(__name__)

html_code = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Puter AI Chatbot</title>
    <script src="https://js.puter.com/v2/"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background-color: #f4f4f4;
        }
        .chat-container {
            width: 90%;
            max-width: 600px;
            height: 80vh;
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
            display: flex;
            flex-direction: column;
        }
        .chat-box {
            flex-grow: 1;
            overflow-y: auto;
            border: 1px solid #ddd;
            padding: 10px;
            background: #fff;
            border-radius: 5px;
            height: 400px;
        }
        .message {
            margin: 10px 0;
            padding: 10px;
            border-radius: 5px;
            max-width: 80%;
        }
        .user-message {
            background: #007BFF;
            color: white;
            text-align: right;
            margin-left: auto;
        }
        .bot-message {
            background: #e9ecef;
            color: black;
            text-align: left;
            margin-right: auto;
        }
        input, button {
            width: 100%;
            padding: 10px;
            margin-top: 10px;
            border: none;
            border-radius: 5px;
        }
        input {
            border: 1px solid #ddd;
        }
        button {
            cursor: pointer;
        }
        #send {
            background-color: #007BFF;
            color: white;
        }
        #speak {
            background-color: #28a745;
            color: white;
        }
        #stop {
            background-color: #dc3545;
            color: white;
        }
        #clear {
            background-color: #6c757d;
            color: white;
        }
    </style>
</head>
<body>

    <div class="chat-container">
        <h2>Puter AI Chatbot</h2>
        <div class="chat-box" id="chat-box"></div>
        <input type="text" id="user-input" placeholder="Type a message..." />
        <button id="send">Send</button>
        <button id="speak" disabled>Speak Response</button>
        <button id="stop" disabled>Stop Speech</button>
        <button id="clear">Clear Chat</button>
    </div>

    <script>
        let currentAudio = null;

        document.getElementById('send').addEventListener('click', () => {
            let userInput = document.getElementById('user-input').value;
            if (userInput.trim() === "") return;

            let chatBox = document.getElementById('chat-box');
            let userMessage = document.createElement("div");
            userMessage.classList.add("message", "user-message");
            userMessage.innerText = userInput;
            chatBox.appendChild(userMessage);
            document.getElementById('user-input').value = "";

            puter.ai.chat(userInput)
                .then(response => {
                    let botMessage = document.createElement("div");
                    botMessage.classList.add("message", "bot-message");
                    botMessage.innerText = response;
                    chatBox.appendChild(botMessage);
                    chatBox.scrollTop = chatBox.scrollHeight;
                    document.getElementById('speak').disabled = false;
                    document.getElementById('stop').disabled = true;
                    document.getElementById('speak').dataset.response = response;
                });
        });

        document.getElementById('speak').addEventListener('click', () => {
            let text = document.getElementById('speak').dataset.response;
            if (text) {
                puter.ai.txt2speech(text).then(audio => {
                    if (currentAudio) {
                        currentAudio.pause();
                        currentAudio = null;
                    }
                    currentAudio = audio;
                    audio.play();
                    document.getElementById('stop').disabled = false;
                });
            }
        });

        document.getElementById('stop').addEventListener('click', () => {
            if (currentAudio) {
                currentAudio.pause();
                currentAudio = null;
                document.getElementById('stop').disabled = true;
            }
        });

        document.getElementById('clear').addEventListener('click', () => {
            document.getElementById('chat-box').innerHTML = "";
            document.getElementById('speak').disabled = true;
            document.getElementById('stop').disabled = true;
            currentAudio = null;
        });
    </script>

</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(html_code)

if __name__ == "__main__":
    app.run(debug=False, port=8080)
