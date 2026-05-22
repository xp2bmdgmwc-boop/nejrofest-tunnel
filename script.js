// State Tunnel Interactive Simulator and Audio Engine

// 1. STATE DEFINITIONS
const STATES = {
    stress: {
        name: 'Стресс / Тревога',
        color: '#0ea5e9',
        carrierFreq: 150,
        beatFreq: 6, // 6 Hz Theta wave (deep relaxation)
        freqLabel: 'Тета-частота гармонизации (150Гц / 156Гц)',
        desc: 'Гармонизация тета-волнами (6 Гц разница). Нейродинамический баланс восстановлен на 94%.',
        visualMode: 'stress'
    },
    apathy: {
        name: 'Усталость / Апатия',
        color: '#f59e0b',
        carrierFreq: 150,
        beatFreq: 12, // 12 Hz Alpha wave (active alert/focus)
        freqLabel: 'Альфа-частота стимуляции (150Гц / 162Гц)',
        desc: 'Стимуляция альфа-активности (12 Гц разница). Когнитивный тонус повышен на 88%.',
        visualMode: 'apathy'
    },
    chaos: {
        name: 'Ментальный Хаос',
        color: '#a855f7',
        carrierFreq: 150,
        beatFreq: 8, // 8 Hz Alpha wave (centering, anxiety relief)
        freqLabel: 'Альфа-частота балансировки (150Гц / 158Гц)',
        desc: 'Центрирование полушарий (8 Гц разница). Ментальный шум снижен на 91%.',
        visualMode: 'chaos'
    },
    balance: {
        name: 'Баланс / Покой',
        color: '#ffffff',
        carrierFreq: 150,
        beatFreq: 0, // Grounding pure single tone (no binaural beat)
        freqLabel: 'Опорный заземляющий тон (150Гц)',
        desc: 'Идеальный баланс достигнут. Выход из шлюза. Пространственная адаптация 100%.',
        visualMode: 'balance'
    }
};

let activeStateKey = 'stress';

// 2. AUDIO ENGINE (Binaural Beats Generator)
let audioCtx = null;
let oscL = null;
let oscR = null;
let panL = null;
let panR = null;
let masterGain = null;
let isAudioPlaying = false;

function initAudio() {
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    
    // Create oscillators
    oscL = audioCtx.createOscillator();
    oscR = audioCtx.createOscillator();
    
    oscL.type = 'sine';
    oscR.type = 'sine';
    
    // Create stereo panners
    panL = audioCtx.createStereoPanner ? audioCtx.createStereoPanner() : audioCtx.createPanner();
    panR = audioCtx.createStereoPanner ? audioCtx.createStereoPanner() : audioCtx.createPanner();
    
    if (panL.pan) {
        panL.pan.value = -1; // Left channel
        panR.pan.value = 1;  // Right channel
    } else {
        // Fallback for older browsers
        panL.panningModel = 'HRTF';
        panR.panningModel = 'HRTF';
        panL.setPosition(-1, 0, 0);
        panR.setPosition(1, 0, 0);
    }
    
    // Create gain node for smooth transitions
    masterGain = audioCtx.createGain();
    masterGain.gain.setValueAtTime(0, audioCtx.currentTime); // Start silent
    
    // Connect nodes
    oscL.connect(panL);
    oscR.connect(panR);
    
    panL.connect(masterGain);
    panR.connect(masterGain);
    
    masterGain.connect(audioCtx.destination);
    
    // Start oscillators
    oscL.start();
    oscR.start();
    
    updateAudioFrequencies();
}

function updateAudioFrequencies() {
    if (!audioCtx) return;
    
    const state = STATES[activeStateKey];
    const targetFL = state.carrierFreq;
    const targetFR = state.carrierFreq + state.beatFreq;
    
    // Smooth transition of frequencies
    oscL.frequency.setTargetAtTime(targetFL, audioCtx.currentTime, 0.3);
    oscR.frequency.setTargetAtTime(targetFR, audioCtx.currentTime, 0.3);
}

function toggleAudio() {
    const audioBtn = document.getElementById('audio-toggle');
    const icon = audioBtn.querySelector('i');
    const span = audioBtn.querySelector('span');
    
    if (!audioCtx) {
        initAudio();
    }
    
    if (isAudioPlaying) {
        // Fade out
        masterGain.gain.setTargetAtTime(0, audioCtx.currentTime, 0.15);
        isAudioPlaying = false;
        icon.className = 'fa-solid fa-volume-xmark';
        span.textContent = 'Включить звук (Частота баланса)';
        audioBtn.classList.remove('playing');
    } else {
        // Resume context if suspended (browser security)
        if (audioCtx.state === 'suspended') {
            audioCtx.resume();
        }
        // Fade in
        masterGain.gain.setTargetAtTime(0.15, audioCtx.currentTime, 0.15);
        isAudioPlaying = true;
        icon.className = 'fa-solid fa-volume-high';
        span.textContent = 'Выключить звук';
        audioBtn.classList.add('playing');
        
        updateAudioFrequencies();
    }
}

// 3. VISUAL ENGINE (Animated Canvas on Main Screen)
const canvas = document.getElementById('visual-canvas');
const ctx = canvas.getContext('2d');
let animationFrameId = null;

// Handle resize
function resizeCanvas() {
    const rect = canvas.parentElement.getBoundingClientRect();
    canvas.width = rect.width;
    canvas.height = rect.height;
}
window.addEventListener('resize', resizeCanvas);
resizeCanvas();

// Visual Elements State
let particles = [];
let waveOffset = 0;

// Initialize particles
function initParticles() {
    particles = [];
    const count = 80;
    for (let i = 0; i < count; i++) {
        particles.push({
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height,
            size: Math.random() * 2 + 1,
            speedX: (Math.random() - 0.5) * 2,
            speedY: (Math.random() - 0.5) * 2,
            alpha: Math.random() * 0.5 + 0.2
        });
    }
}
initParticles();

// Render loop
function drawVisualizer() {
    ctx.fillStyle = 'rgba(2, 2, 4, 0.15)'; // Trail effect
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    const stateColor = STATES[activeStateKey].color;
    
    if (activeStateKey === 'stress') {
        // Stress Visual: Jagged, high speed waves + fast erratic dots
        ctx.strokeStyle = stateColor;
        ctx.lineWidth = 1.5;
        
        ctx.beginPath();
        for (let x = 0; x < canvas.width; x++) {
            const y = canvas.height / 2 + 
                      Math.sin(x * 0.02 + waveOffset) * 40 * Math.sin(x * 0.005) + 
                      Math.cos(x * 0.08 + waveOffset * 2) * 10;
            if (x === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        }
        ctx.stroke();
        
        // Rapid dots
        particles.forEach(p => {
            p.speedX = (Math.random() - 0.5) * 6;
            p.speedY = (Math.random() - 0.5) * 6;
            p.x += p.speedX;
            p.y += p.speedY;
            if (p.x < 0 || p.x > canvas.width) p.x = Math.random() * canvas.width;
            if (p.y < 0 || p.y > canvas.height) p.y = Math.random() * canvas.height;
            
            ctx.fillStyle = stateColor;
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
            ctx.fill();
        });
        
        waveOffset += 0.15;
        
    } else if (activeStateKey === 'apathy') {
        // Apathy Visual: Heavy sluggish drift, large slow waves
        ctx.fillStyle = 'rgba(245, 158, 11, 0.02)';
        
        // Large slow wave
        ctx.strokeStyle = stateColor;
        ctx.lineWidth = 3;
        ctx.beginPath();
        for (let x = 0; x < canvas.width; x++) {
            const y = canvas.height / 2 + Math.sin(x * 0.005 + waveOffset) * 60;
            if (x === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        }
        ctx.stroke();
        
        // Sluggish floating dust
        particles.forEach(p => {
            p.speedX = 0.2;
            p.speedY = Math.sin(p.x * 0.01) * 0.5;
            p.x += p.x > canvas.width ? -canvas.width : p.speedX;
            p.y += p.speedY;
            
            ctx.fillStyle = stateColor;
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.size * 2, 0, Math.PI * 2);
            ctx.fill();
        });
        
        waveOffset += 0.01;
        
    } else if (activeStateKey === 'chaos') {
        // Chaos Visual: Intersecting geometry, starbursts/symmetrical structures
        ctx.strokeStyle = stateColor;
        ctx.lineWidth = 1;
        
        const centerX = canvas.width / 2;
        const centerY = canvas.height / 2;
        
        ctx.save();
        ctx.translate(centerX, centerY);
        ctx.rotate(waveOffset * 0.5);
        
        ctx.beginPath();
        for (let i = 0; i < 8; i++) {
            ctx.rotate(Math.PI / 4);
            ctx.moveTo(0, 0);
            ctx.lineTo(Math.sin(waveOffset) * 120 + 50, Math.cos(waveOffset) * 120 + 50);
        }
        ctx.stroke();
        ctx.restore();
        
        // Swirling chaos particles
        particles.forEach(p => {
            const dx = p.x - centerX;
            const dy = p.y - centerY;
            const dist = Math.sqrt(dx*dx + dy*dy);
            const angle = Math.atan2(dy, dx) + 0.02;
            p.x = centerX + Math.cos(angle) * (dist - 0.2);
            p.y = centerY + Math.sin(angle) * (dist - 0.2);
            
            if (dist < 10) {
                p.x = Math.random() * canvas.width;
                p.y = Math.random() * canvas.height;
            }
            
            ctx.fillStyle = stateColor;
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
            ctx.fill();
        });
        
        waveOffset += 0.02;
        
    } else if (activeStateKey === 'balance') {
        // Balance Visual: Symmetrical, breathing circles, perfect calmness
        const centerX = canvas.width / 2;
        const centerY = canvas.height / 2;
        const radius = 100 + Math.sin(waveOffset) * 20;
        
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.4)';
        ctx.lineWidth = 1;
        
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
        ctx.stroke();
        
        // Second concentric ring
        ctx.strokeStyle = 'rgba(212, 175, 55, 0.3)';
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius * 0.7, 0, Math.PI * 2);
        ctx.stroke();
        
        // Still, slowly fading ambient particles
        particles.forEach(p => {
            p.x += (Math.random() - 0.5) * 0.2;
            p.y += (Math.random() - 0.5) * 0.2;
            
            ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
            ctx.fill();
        });
        
        waveOffset += 0.015;
    }
    
    animationFrameId = requestAnimationFrame(drawVisualizer);
}
drawVisualizer();

// 4. CHART ENGINE (Souvenir Mini-Chart)
const chartCanvas = document.getElementById('chart-canvas');
const chartCtx = chartCanvas.getContext('2d');
let stateHistory = [70, 70, 70, 70, 70, 70, 70]; // Default mock data representing stress level

function drawChart() {
    chartCtx.clearRect(0, 0, chartCanvas.width, chartCanvas.height);
    
    // Draw background grid lines
    chartCtx.strokeStyle = 'rgba(255,255,255,0.05)';
    chartCtx.lineWidth = 1;
    for (let i = 1; i <= 3; i++) {
        const y = (chartCanvas.height / 4) * i;
        chartCtx.beginPath();
        chartCtx.moveTo(0, y);
        chartCtx.lineTo(chartCanvas.width, y);
        chartCtx.stroke();
    }
    
    // Smooth transition of values
    let targetVal = 70; // Stress
    if (activeStateKey === 'apathy') targetVal = 50;
    else if (activeStateKey === 'chaos') targetVal = 80;
    else if (activeStateKey === 'balance') targetVal = 10;
    
    // Add value and slide
    stateHistory.push(targetVal);
    if (stateHistory.length > 25) {
        stateHistory.shift();
    }
    
    // Plot line
    chartCtx.beginPath();
    chartCtx.lineWidth = 2.5;
    const gradient = chartCtx.createLinearGradient(0, 0, chartCanvas.width, 0);
    gradient.addColorStop(0, '#0ea5e9');
    gradient.addColorStop(0.5, '#a855f7');
    gradient.addColorStop(1, STATES[activeStateKey].color);
    
    chartCtx.strokeStyle = gradient;
    
    const step = chartCanvas.width / (stateHistory.length - 1);
    for (let i = 0; i < stateHistory.length; i++) {
        // Invert so high stress is high up, low stress is near bottom
        const y = chartCanvas.height - (stateHistory[i] / 100) * (chartCanvas.height - 10) - 5;
        const x = i * step;
        
        if (i === 0) chartCtx.moveTo(x, y);
        else chartCtx.lineTo(x, y);
    }
    chartCtx.stroke();
    
    // Area fill
    chartCtx.lineTo(chartCanvas.width, chartCanvas.height);
    chartCtx.lineTo(0, chartCanvas.height);
    const fillGradient = chartCtx.createLinearGradient(0, 0, 0, chartCanvas.height);
    fillGradient.addColorStop(0, 'rgba(212, 175, 55, 0.1)');
    fillGradient.addColorStop(1, 'rgba(212, 175, 55, 0)');
    chartCtx.fillStyle = fillGradient;
    chartCtx.fill();
}
setInterval(drawChart, 200);

// 5. INTERACTIVE EVENT HANDLERS
const stateButtons = document.querySelectorAll('.btn-state');

stateButtons.forEach(btn => {
    btn.addEventListener('click', () => {
        // Toggle active button
        stateButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        // Update active state
        activeStateKey = btn.dataset.state;
        const state = STATES[activeStateKey];
        
        // Update text labels
        document.getElementById('current-state-val').textContent = state.name;
        document.getElementById('frequency-val').textContent = state.freqLabel;
        document.getElementById('souvenir-desc').textContent = state.desc;
        
        // Update Glow Backgrounds based on state
        const glow1 = document.getElementById('glow-1');
        glow1.style.background = `radial-gradient(circle, ${state.color}1c 0%, rgba(6,6,10,0) 70%)`;
        
        // Sync Audio engine
        updateAudioFrequencies();
        
        // Trigger ripples/micro-interactions in sidebar
        const pulse = document.querySelector('.pulse-ring');
        if (pulse) {
            pulse.style.backgroundColor = `${state.color}2b`;
        }
    });
});

// Sound Toggle click
document.getElementById('audio-toggle').addEventListener('click', toggleAudio);

// MODAL FUNCTIONALITY (QR Code modal)
const modal = document.getElementById('qr-modal');
const openModalBtn = document.getElementById('btn-download-souvenir');
const closeModalElements = document.querySelectorAll('.close-modal, #btn-close-modal');

openModalBtn.addEventListener('click', () => {
    modal.classList.add('active');
});

closeModalElements.forEach(elem => {
    elem.addEventListener('click', () => {
        modal.classList.remove('active');
    });
});

// Close modal when clicking outside content
modal.addEventListener('click', (e) => {
    if (e.target === modal) {
        modal.classList.remove('active');
    }
});
