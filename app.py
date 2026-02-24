import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="F1 Reflex Timer", layout="wide")

st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .block-container {
            padding-top: 0rem;
            padding-bottom: 0rem;
        }
    </style>
""", unsafe_allow_html=True)

html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>F1 Reaction Timer</title>
    <style>
        /* --- BASE STYLES (LIGHT MODE) --- */
        body {
            margin: 0;
            height: 95vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            font-family: Arial, sans-serif;
            background-color: #ffffff;
            color: #000000;
            user-select: none; 
            cursor: pointer;
            overflow: hidden;
            outline: none; 
            transition: background-color 0.3s, color 0.3s;
        }

        .lights-board { display: flex; gap: 15px; margin-bottom: 20px; }
        .light-column { background-color: #111; padding: 10px; border-radius: 10px; display: flex; flex-direction: column; gap: 10px; }
        .light { width: 60px; height: 60px; border-radius: 50%; background-color: #333; transition: background-color 0.05s; }
        .light.red { background-color: #ff0000; box-shadow: 0 0 20px #ff0000; }
        .message { font-size: 1.2rem; color: #555; height: 24px; text-align: center; padding: 0 10px; transition: color 0.3s; }
        .timer-display { font-size: 8rem; font-weight: normal; margin: 10px 0; height: 150px; display: flex; align-items: center; justify-content: center; }
        .stats { font-size: 1rem; color: #333; transition: color 0.3s; }

        /* --- THEME TOGGLE BUTTON --- */
        .theme-toggle {
            position: absolute;
            top: 20px;
            right: 20px;
            padding: 8px 16px;
            border-radius: 20px;
            border: none;
            background-color: #f0f0f0;
            color: #333;
            font-weight: bold;
            cursor: pointer;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            transition: all 0.3s;
            z-index: 100;
        }
        .theme-toggle:hover { background-color: #e0e0e0; }

        /* --- DARK MODE STYLES --- */
        body.dark-mode {
            background-color: #121212;
            color: #ffffff;
        }
        body.dark-mode .message { color: #aaaaaa; }
        body.dark-mode .stats { color: #dddddd; }
        body.dark-mode .theme-toggle {
            background-color: #333333;
            color: #ffffff;
            box-shadow: 0 2px 5px rgba(255,255,255,0.1);
        }
        body.dark-mode .theme-toggle:hover { background-color: #444444; }
        /* Make the "off" lights slightly darker so they blend better in dark mode */
        body.dark-mode .light { background-color: #222222; }

        /* --- MOBILE SCREEN SUPPORT --- */
        @media (max-width: 600px) {
            .lights-board { gap: 8px; }
            .light-column { padding: 6px; gap: 6px; border-radius: 8px; }
            .light { width: 45px; height: 45px; }
            .timer-display { font-size: 5rem; height: 100px; }
            .message { font-size: 1rem; }
            .theme-toggle { top: 10px; right: 10px; padding: 6px 12px; font-size: 0.9rem; }
        }
        
        @media (max-width: 380px) {
            .light { width: 35px; height: 35px; }
            .timer-display { font-size: 4rem; }
        }
    </style>
</head>
<body tabindex="0">

    <button id="theme-toggle" class="theme-toggle">🌙 Dark</button>

    <div class="lights-board" id="lights-board"></div>
    <div class="message" id="message">Click here once, then press SPACE when ready.</div>
    <div class="timer-display" id="timer-display">00.000</div>
    <div class="stats">Your best: <span id="best-time">00.000</span></div>

    <script>
        window.onload = () => window.focus();
        document.body.addEventListener('mouseenter', () => window.focus());

        // --- THEME TOGGLE LOGIC ---
        const themeToggle = document.getElementById('theme-toggle');
        themeToggle.addEventListener('click', (e) => {
            // CRITICAL: Stop the click from bubbling down to the body and triggering the game!
            e.stopPropagation(); 
            
            document.body.classList.toggle('dark-mode');
            if (document.body.classList.contains('dark-mode')) {
                themeToggle.textContent = '☀️ Light';
            } else {
                themeToggle.textContent = '🌙 Dark';
            }
        });

        // --- GAME LOGIC ---
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
            document.querySelectorAll('.light.red').forEach(light => light.classList.remove('red'));
            activeColumns = 0;
        }

        function turnOnColumn(colIndex) {
            document.querySelectorAll(`.light[data-col="${colIndex}"]`).forEach(light => light.classList.add('red'));
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

components.html(html_content, height=800, scrolling=False)