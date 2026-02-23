import streamlit as st
import streamlit.components.v1 as components

# Configure the Streamlit page to look more like a native app
st.set_page_config(page_title="F1 Reflex Timer", layout="wide")

# Hide standard Streamlit header and footer for a cleaner look
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        /* Remove padding to let the game take the full screen */
        .block-container {
            padding-top: 0rem;
            padding-bottom: 0rem;
        }
    </style>
""", unsafe_allow_html=True)

# The updated HTML, CSS (with mobile support), and JS
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>F1 Reaction Timer</title>
    <style>
        body {
            margin: 0;
            height: 95vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            font-family: Arial, sans-serif;
            background-color: #fff;
            user-select: none; 
            cursor: pointer;
            overflow: hidden; /* Prevent scrolling on mobile */
        }

        .lights-board {
            display: flex;
            gap: 15px;
            margin-bottom: 20px;
        }

        .light-column {
            background-color: #111;
            padding: 10px;
            border-radius: 10px;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        .light {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background-color: #333;
            transition: background-color 0.05s;
        }

        .light.red {
            background-color: #ff0000;
            box-shadow: 0 0 20px #ff0000;
        }

        .message {
            font-size: 1.2rem;
            color: #555;
            height: 24px;
            text-align: center;
            padding: 0 10px;
        }

        .timer-display {
            font-size: 8rem;
            font-weight: normal;
            margin: 10px 0;
            height: 150px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .stats {
            font-size: 1rem;
            color: #333;
        }

        /* --- MOBILE SCREEN SUPPORT --- */
        @media (max-width: 600px) {
            .lights-board {
                gap: 8px;
            }
            .light-column {
                padding: 6px;
                gap: 6px;
                border-radius: 8px;
            }
            .light {
                width: 45px;
                height: 45px;
            }
            .timer-display {
                font-size: 5rem;
                height: 100px;
            }
            .message {
                font-size: 1rem;
            }
        }
        
        @media (max-width: 380px) {
            .light { width: 35px; height: 35px; }
            .timer-display { font-size: 4rem; }
        }
    </style>
</head>
<body>

    <div class="lights-board" id="lights-board"></div>
    <div class="message" id="message">Tap, click, or press SPACE when ready.</div>
    <div class="timer-display" id="timer-display">00.000</div>
    <div class="stats">Your best: <span id="best-time">00.000</span></div>

    <script>
        const board = document.getElementById('lights-board');
        const timerDisplay = document.getElementById('timer-display');
        const messageDisplay = document.getElementById('message');
        const bestTimeDisplay = document.getElementById('best-time');

        let state = 'waiting'; 
        let startTime = 0;
        let bestTime = Infinity;
        let sequenceTimeouts = [];
        let randomDropTimeout = null;
        let activeColumns = 0;

        for (let i = 0; i < 5; i++) {
            const column = document.createElement('div');
            column.className = 'light-column';
            for (let j = 0; j < 4; j++) {
                const light = document.createElement('div');
                light.className = 'light';
                if (j >= 2) light.dataset.col = i; 
                column.appendChild(light);
            }
            board.appendChild(column);
        }

        function turnOffAllLights() {
            document.querySelectorAll('.light.red').forEach(light => {
                light.classList.remove('red');
            });
            activeColumns = 0;
        }

        function turnOnColumn(colIndex) {
            const lights = document.querySelectorAll(`.light[data-col="${colIndex}"]`);
            lights.forEach(light => light.classList.add('red'));
        }

        function clearAllTimeouts() {
            sequenceTimeouts.forEach(clearTimeout);
            clearTimeout(randomDropTimeout);
            sequenceTimeouts = [];
        }

        function startSequence() {
            state = 'sequencing';
            timerDisplay.textContent = '00.000';
            messageDisplay.textContent = "Wait for the lights to go out...";
            turnOffAllLights();
            clearAllTimeouts();

            for (let i = 0; i < 5; i++) {
                sequenceTimeouts.push(setTimeout(() => {
                    turnOnColumn(i);
                    activeColumns++;
                    
                    if (activeColumns === 5) {
                        state = 'holding';
                        const randomDelay = Math.random() * 3500 + 3500;
                        randomDropTimeout = setTimeout(startTimer, randomDelay);
                    }
                }, i * 1000 + 1000));
            }
        }

        function startTimer() {
            state = 'timing';
            turnOffAllLights();
            startTime = performance.now(); 
            messageDisplay.textContent = "GO!";
        }

        function handleJumpStart() {
            state = 'result';
            clearAllTimeouts();
            timerDisplay.textContent = "JUMP START!";
            messageDisplay.textContent = "You reacted too early! Try again.";
        }

        function finishRace() {
            state = 'result';
            const reactionTime = (performance.now() - startTime) / 1000;
            const formattedTime = reactionTime.toFixed(3);
            
            timerDisplay.textContent = reactionTime < 10 ? `0${formattedTime}` : formattedTime;
            messageDisplay.textContent = "Try again.";

            if (reactionTime < bestTime) {
                bestTime = reactionTime;
                bestTimeDisplay.textContent = reactionTime < 10 ? `0${formattedTime}` : formattedTime;
            }
        }

        function handleInteraction(e) {
            if (e && e.type === 'keydown') {
                if (e.code !== 'Space' || e.repeat) return;
                e.preventDefault(); 
            } else if (e) {
                e.preventDefault();
            }

            switch (state) {
                case 'waiting':
                case 'result':
                    startSequence();
                    break;
                case 'sequencing':
                case 'holding':
                    handleJumpStart();
                    break;
                case 'timing':
                    finishRace();
                    break;
            }
        }

        document.body.addEventListener('mousedown', handleInteraction);
        document.body.addEventListener('touchstart', handleInteraction, { passive: false });
        document.addEventListener('keydown', handleInteraction);
    </script>
</body>
</html>
"""

# Render the HTML inside the Streamlit appp
components.html(html_content, height=800, scrolling=False)