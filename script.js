// 1. LOCALIZATION SYSTEM
const isEn = document.documentElement.lang === 'en';

const LOC = {
    ru: {
        states: {
            stress: {
                name: 'Стресс / Тревога',
                freqLabel: 'Тета-частота гармонизации (150Гц / 156Гц)',
                desc: 'Гармонизация тета-волнами (6 Гц разница). Нейродинамический баланс восстановлен на 94%.'
            },
            apathy: {
                name: 'Усталость / Апатия',
                freqLabel: 'Альфа-частота стимуляции (150Гц / 162Гц)',
                desc: 'Стимуляция альфа-активности (12 Гц разница). Когнитивный тонус повышен на 88%.'
            },
            chaos: {
                name: 'Ментальный Хаос',
                freqLabel: 'Альфа-частота балансировки (150Гц / 158Гц)',
                desc: 'Центрирование полушарий (8 Гц разница). Ментальный шум снижен на 91%.'
            },
            balance: {
                name: 'Баланс / Покой',
                freqLabel: 'Опорный заземляющий тон (150Гц)',
                desc: 'Идеальный баланс достигнут. Выход из шлюза. Пространственная адаптация 100%.'
            }
        },
        audioPlay: 'Включить звук (Частота баланса)',
        audioStop: 'Выключить звук',
        metro: {
            sokol: 'Сокольническая (Красная)',
            zamos: 'Замоскворецкая (Зеленая)',
            koltso: 'Кольцевая (Коричневая)',
            tagan: 'Таганско-Краснопресненская (Фиолетовая)'
        },
        nodes: {
            ges2: 'ГЭС-2 / Патриарший мост',
            city: 'Москва-Сити',
            zaryadye: 'Зарядье / Парящий мост',
            krymsky: 'Крымский мост / Парк Культуры',
            belorusskaya: 'Белорусский узел',
            taganskaya: 'Таганский узел'
        },
        status: {
            sync: 'СИНХРОНИЗАЦИЯ: 100%',
            stress: 'ШУМ: ВЫСОКИЙ (СБРОС)',
            apathy: 'ТОНУС: НИЗКИЙ (АКТИВАЦИЯ)',
            chaos: 'ШУМ: 91% (БАЛАНСИРОВКА)',
            balance: 'СОСТОЯНИЕ: ИДЕАЛЬНОЕ'
        }
    },
    en: {
        states: {
            stress: {
                name: 'Stress / Anxiety',
                freqLabel: 'Theta frequency of harmonization (150Hz / 156Hz)',
                desc: 'Harmonization by theta waves (6 Hz difference). Neurodynamic balance restored to 94%.'
            },
            apathy: {
                name: 'Fatigue / Apathy',
                freqLabel: 'Alpha frequency of stimulation (150Hz / 162Hz)',
                desc: 'Stimulation of alpha activity (12 Hz difference). Cognitive tone increased by 88%.'
            },
            chaos: {
                name: 'Mental Chaos',
                freqLabel: 'Alpha frequency of balancing (150Hz / 158Hz)',
                desc: 'Centering of hemispheres (8 Hz difference). Mental noise reduced by 91%.'
            },
            balance: {
                name: 'Balance / Peace',
                freqLabel: 'Grounding reference tone (150Hz)',
                desc: 'Perfect balance achieved. Exit from the gateway. Spatial adaptation 100%.'
            }
        },
        audioPlay: 'Turn on sound (Balance frequency)',
        audioStop: 'Turn off sound',
        metro: {
            sokol: 'Sokolnicheskaya (Red)',
            zamos: 'Zamoskvoretskaya (Green)',
            koltso: 'Koltsevaya (Brown)',
            tagan: 'Tagansko-Krasnopresnenskaya (Purple)'
        },
        nodes: {
            ges2: 'GES-2 / Patriarchal Bridge',
            city: 'Moscow-City',
            zaryadye: 'Zaryadye / Floating Bridge',
            krymsky: 'Krymsky Bridge / Gorky Park',
            belorusskaya: 'Belorusskaya Interchange',
            taganskaya: 'Taganskaya Interchange'
        },
        status: {
            sync: 'SYNCHRONIZATION: 100%',
            stress: 'NOISE: HIGH (RESET)',
            apathy: 'TONE: LOW (ACTIVATION)',
            chaos: 'NOISE: 91% (BALANCING)',
            balance: 'STATE: PERFECT'
        }
    }
};

const lang = isEn ? 'en' : 'ru';
const t = LOC[lang];

// 1. STATE DEFINITIONS
const STATES = {
    stress: {
        name: t.states.stress.name,
        color: '#0ea5e9',
        carrierFreq: 150,
        beatFreq: 6, // 6 Hz Theta wave (deep relaxation)
        freqLabel: t.states.stress.freqLabel,
        desc: t.states.stress.desc,
        visualMode: 'stress'
    },
    apathy: {
        name: t.states.apathy.name,
        color: '#f59e0b',
        carrierFreq: 150,
        beatFreq: 12, // 12 Hz Alpha wave (active alert/focus)
        freqLabel: t.states.apathy.freqLabel,
        desc: t.states.apathy.desc,
        visualMode: 'apathy'
    },
    chaos: {
        name: t.states.chaos.name,
        color: '#a855f7',
        carrierFreq: 150,
        beatFreq: 8, // 8 Hz Alpha wave (centering, anxiety relief)
        freqLabel: t.states.chaos.freqLabel,
        desc: t.states.chaos.desc,
        visualMode: 'chaos'
    },
    balance: {
        name: t.states.balance.name,
        color: '#ffffff',
        carrierFreq: 150,
        beatFreq: 0, // Grounding pure single tone (no binaural beat)
        freqLabel: t.states.balance.freqLabel,
        desc: t.states.balance.desc,
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
        span.textContent = t.audioPlay;
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
        span.textContent = t.audioStop;
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
        
        // Update telemetry data dynamically
        const rppgElem = document.getElementById('telemetry-rppg');
        const hrElem = document.getElementById('telemetry-hr');
        const phaseElem = document.getElementById('telemetry-phase');
        
        if (rppgElem && hrElem && phaseElem) {
            if (activeStateKey === 'stress') {
                rppgElem.textContent = '96%';
                hrElem.textContent = '115 bpm';
                phaseElem.textContent = '6Hz (Theta)';
            } else if (activeStateKey === 'apathy') {
                rppgElem.textContent = '88%';
                hrElem.textContent = '58 bpm';
                phaseElem.textContent = '12Hz (Alpha)';
            } else if (activeStateKey === 'chaos') {
                rppgElem.textContent = '92%';
                hrElem.textContent = '89 bpm';
                phaseElem.textContent = '8Hz (Alpha)';
            } else if (activeStateKey === 'balance') {
                rppgElem.textContent = '99%';
                hrElem.textContent = '68 bpm';
                phaseElem.textContent = 'PURE TONE';
            }
        }
        
        // Update Glow Backgrounds based on state
        const glow1 = document.getElementById('glow-1');
        if (glow1) {
            glow1.style.background = `radial-gradient(circle, ${state.color}1c 0%, rgba(6,6,10,0) 70%)`;
        }
        
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

if (openModalBtn && modal) {
    openModalBtn.addEventListener('click', () => {
        modal.classList.add('active');
    });

    closeModalElements.forEach(elem => {
        elem.addEventListener('click', () => {
            modal.classList.remove('active');
        });
    });

    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.remove('active');
        }
    });
}

// ==========================================================================
// 6. MATRIX PILL PORTAL & TRANSIT VIDEO SYSTEM
// ==========================================================================

const matrixCanvas = document.getElementById('matrix-rain-canvas');
if (matrixCanvas) {
    const mCtx = matrixCanvas.getContext('2d');
    let mWidth = matrixCanvas.width = window.innerWidth;
    let mHeight = matrixCanvas.height = window.innerHeight;
    
    window.addEventListener('resize', () => {
        mWidth = matrixCanvas.width = window.innerWidth;
        mHeight = matrixCanvas.height = window.innerHeight;
        mColumns = Math.floor(mWidth / 20);
        mDrops.length = 0;
        for (let x = 0; x < mColumns; x++) mDrops[x] = 1;
    });

    const characters = '0101010101010101010101010101010101';
    const mFontSize = 14;
    let mColumns = Math.floor(mWidth / 20);
    const mDrops = [];
    for (let x = 0; x < mColumns; x++) {
        mDrops[x] = Math.random() * -100; // Staggered start positions
    }

    let targetMatrixColor = { r: 16, g: 185, b: 129 }; // Default Matrix Green
    let currentMatrixColor = { r: 16, g: 185, b: 129 };

    function lerp(start, end, amt) {
        return (1 - amt) * start + amt * end;
    }

    function drawMatrixRain() {
        mCtx.fillStyle = 'rgba(2, 2, 4, 0.08)';
        mCtx.fillRect(0, 0, mWidth, mHeight);

        // Interpolate colors smoothly
        currentMatrixColor.r = lerp(currentMatrixColor.r, targetMatrixColor.r, 0.08);
        currentMatrixColor.g = lerp(currentMatrixColor.g, targetMatrixColor.g, 0.08);
        currentMatrixColor.b = lerp(currentMatrixColor.b, targetMatrixColor.b, 0.08);
        
        mCtx.fillStyle = `rgb(${Math.round(currentMatrixColor.r)}, ${Math.round(currentMatrixColor.g)}, ${Math.round(currentMatrixColor.b)})`;
        mCtx.font = mFontSize + 'px monospace';

        for (let i = 0; i < mDrops.length; i++) {
            const text = characters.charAt(Math.floor(Math.random() * characters.length));
            mCtx.fillText(text, i * 20, mDrops[i] * mFontSize);

            if (mDrops[i] * mFontSize > mHeight && Math.random() > 0.975) {
                mDrops[i] = 0;
            }
            mDrops[i]++;
        }
        requestAnimationFrame(drawMatrixRain);
    }
    drawMatrixRain();

    // Hover states for the pills to change the matrix rain color
    const redBtn = document.getElementById('pill-red-btn');
    const blueBtn = document.getElementById('pill-blue-btn');

    if (redBtn && blueBtn) {
        redBtn.addEventListener('mouseenter', () => {
            targetMatrixColor = { r: 239, g: 68, b: 68 }; // Neon Red
            matrixCanvas.style.opacity = '0.3';
        });
        redBtn.addEventListener('mouseleave', () => {
            targetMatrixColor = { r: 16, g: 185, b: 129 }; // Restore Green
            matrixCanvas.style.opacity = '0.15';
        });

        blueBtn.addEventListener('mouseenter', () => {
            targetMatrixColor = { r: 14, g: 165, b: 233 }; // Neon Blue
            matrixCanvas.style.opacity = '0.3';
        });
        blueBtn.addEventListener('mouseleave', () => {
            targetMatrixColor = { r: 16, g: 185, b: 129 }; // Restore Green
            matrixCanvas.style.opacity = '0.15';
        });
    }
}

// Choice Routing & Video Player
const introVideoOverlay = document.getElementById('intro-video-overlay');
const introVideo = document.getElementById('intro-video');
const skipIntroBtn = document.getElementById('skip-intro-btn');
let chosenStateKey = 'balance';

function handlePillChoice(stateKey) {
    chosenStateKey = stateKey;

    // 1. Initialize audio context IMMEDIATELY on user click (gesture approval)
    if (!audioCtx) {
        initAudio();
    } else if (audioCtx.state === 'suspended') {
        audioCtx.resume();
    }
    
    // Set simulator frequencies based on choice but keep muted during transit
    updateAudioFrequencies();

    // 2. Animate and fade out Matrix portal
    const matrixPortal = document.getElementById('matrix-portal');
    if (matrixPortal) {
        matrixPortal.classList.add('fade-out');
    }

    // 3. Open Video Overlay and Play
    if (introVideoOverlay) {
        introVideoOverlay.classList.add('active');
    }

    if (introVideo) {
        introVideo.play().catch(err => {
            console.warn("Video play blocked, skipping transition", err);
            exitIntroPortal();
        });
    }
}

function exitIntroPortal() {
    if (introVideo) {
        introVideo.pause();
    }

    // Fade out video overlay
    if (introVideoOverlay) {
        introVideoOverlay.classList.remove('active');
        setTimeout(() => {
            introVideoOverlay.style.display = 'none';
            const portal = document.getElementById('matrix-portal');
            if (portal) portal.style.display = 'none';
        }, 800);
    }

    // Unlock page scroll
    document.body.classList.remove('scroll-locked');
    document.body.classList.add('simulation-active');

    // Programmatically select state in simulator
    const btn = document.querySelector(`.btn-state[data-state="${chosenStateKey}"]`);
    if (btn) {
        btn.click();
    }

    // Unmute and start audio playing immediately!
    if (!isAudioPlaying) {
        toggleAudio();
    }
}

document.getElementById('start-simulation-btn')?.addEventListener('click', () => {
    const startScreen = document.getElementById('matrix-start-screen');
    const choiceScreen = document.getElementById('matrix-choice-screen');
    
    if (startScreen && choiceScreen) {
        startScreen.style.opacity = '0';
        setTimeout(() => {
            startScreen.style.display = 'none';
            choiceScreen.style.display = 'flex';
            // Trigger reflow to ensure the transition works
            choiceScreen.offsetHeight;
            choiceScreen.style.opacity = '1';
            
            // Activate the Matrix Rain canvas (fade it in)
            if (matrixCanvas) {
                matrixCanvas.style.opacity = '0.15';
            }
        }, 500);
    }
});

document.getElementById('pill-red-btn')?.addEventListener('click', () => handlePillChoice('stress'));
document.getElementById('pill-blue-btn')?.addEventListener('click', () => handlePillChoice('balance'));
skipIntroBtn?.addEventListener('click', exitIntroPortal);
introVideo?.addEventListener('ended', exitIntroPortal);



// ==========================================================================
// 7. CITY SCALE: INTERACTIVE MAP CANVAS ENGINE (METRO & CITY NETWORKS)
// ==========================================================================

const cityCanvas = document.getElementById('city-network-canvas');
if (cityCanvas) {
    const cCtx = cityCanvas.getContext('2d');
    let cWidth = cityCanvas.width = cityCanvas.parentElement.clientWidth;
    let cHeight = cityCanvas.height = 320;

    function resizeCityCanvas() {
        if (cityCanvas.parentElement) {
            cWidth = cityCanvas.width = cityCanvas.parentElement.clientWidth;
            cHeight = cityCanvas.height = cityCanvas.parentElement.clientHeight || 320;
        }
    }
    window.addEventListener('resize', resizeCityCanvas);
    
    // Generate Moskva River path coordinates snaking through canvas
    const getRiverPath = () => {
        const points = [];
        const segments = 100;
        for (let i = 0; i <= segments; i++) {
            const t = i / segments;
            const x = t * cWidth;
            // Snaking river equation
            const y = cHeight * 0.52 + Math.sin(t * Math.PI * 2.4) * (cHeight * 0.22) + Math.cos(t * Math.PI * 1.1) * (cHeight * 0.08);
            points.push({ x, y });
        }
        return points;
    };

    // Metro Lines path coordinates
    const getMetroLines = (centerX, centerY) => {
        return [
            {
                name: t.metro.sokol,
                color: '#ef4444',
                points: [
                    { x: centerX - cWidth * 0.38, y: centerY + cHeight * 0.38 },
                    { x: centerX - cWidth * 0.16, y: centerY + cHeight * 0.16 },
                    { x: centerX, y: centerY },
                    { x: centerX + cWidth * 0.16, y: centerY - cHeight * 0.16 },
                    { x: centerX + cWidth * 0.38, y: centerY - cHeight * 0.38 }
                ]
            },
            {
                name: t.metro.zamos,
                color: '#10b981',
                points: [
                    { x: centerX - cWidth * 0.22, y: centerY - cHeight * 0.4 },
                    { x: centerX - cWidth * 0.08, y: centerY - cHeight * 0.18 },
                    { x: centerX, y: centerY },
                    { x: centerX + cWidth * 0.06, y: centerY + cHeight * 0.2 },
                    { x: centerX + cWidth * 0.12, y: centerY + cHeight * 0.4 }
                ]
            },
            {
                name: t.metro.koltso,
                color: '#8b5a2b',
                isRing: true,
                radiusX: cWidth * 0.14,
                radiusY: cHeight * 0.28,
                centerX: centerX,
                centerY: centerY
            },
            {
                name: t.metro.tagan,
                color: '#a855f7',
                points: [
                    { x: centerX - cWidth * 0.35, y: centerY - cHeight * 0.28 },
                    { x: centerX - cWidth * 0.14, y: centerY - cHeight * 0.12 },
                    { x: centerX + cWidth * 0.06, y: centerY + cHeight * 0.06 },
                    { x: centerX + cWidth * 0.25, y: centerY + cHeight * 0.28 }
                ]
            }
        ];
    };

    // City Nodes (Bridges, City towers, hubs)
    const getHubNodes = (centerX, centerY) => {
        return [
            { id: 'ges2', name: t.nodes.ges2, x: centerX + cWidth * 0.01, y: centerY + cHeight * 0.08, pulseSize: 8, isCore: true },
            { id: 'city', name: t.nodes.city, x: centerX - cWidth * 0.26, y: centerY + cHeight * 0.02, pulseSize: 6, isCore: false },
            { id: 'zaryadye', name: t.nodes.zaryadye, x: centerX + cWidth * 0.13, y: centerY + cHeight * 0.04, pulseSize: 5, isCore: false },
            { id: 'krymsky', name: t.nodes.krymsky, x: centerX - cWidth * 0.08, y: centerY + cHeight * 0.17, pulseSize: 5, isCore: false },
            { id: 'belorusskaya', name: t.nodes.belorusskaya, x: centerX - cWidth * 0.12, y: centerY - cHeight * 0.22, pulseSize: 4, isCore: false },
            { id: 'taganskaya', name: t.nodes.taganskaya, x: centerX + cWidth * 0.16, y: centerY + cHeight * 0.18, pulseSize: 4, isCore: false }
        ];
    };

    // Signal Particle class
    class SignalParticle {
        constructor(path, color, speed, isRing = false, ringData = null) {
            this.path = path;
            this.color = color;
            this.speed = speed;
            this.isRing = isRing;
            this.ringData = ringData;
            this.size = Math.random() * 2 + 1.2;
            
            if (this.isRing) {
                this.angle = Math.random() * Math.PI * 2;
                this.x = ringData.centerX + Math.cos(this.angle) * ringData.radiusX;
                this.y = ringData.centerY + Math.sin(this.angle) * ringData.radiusY;
            } else {
                this.progress = Math.random();
                this.updatePosition();
            }
        }

        updatePosition() {
            if (this.isRing) {
                this.angle += (this.speed * 0.012);
                if (this.angle > Math.PI * 2) this.angle -= Math.PI * 2;
                this.x = this.ringData.centerX + Math.cos(this.angle) * this.ringData.radiusX;
                this.y = this.ringData.centerY + Math.sin(this.angle) * this.ringData.radiusY;
            } else {
                const totalPoints = this.path.length;
                const segmentProgress = this.progress * (totalPoints - 1);
                const startIndex = Math.floor(segmentProgress);
                const endIndex = Math.min(startIndex + 1, totalPoints - 1);
                const t = segmentProgress - startIndex;

                const p1 = this.path[startIndex];
                const p2 = this.path[endIndex];

                if (p1 && p2) {
                    this.x = p1.x + (p2.x - p1.x) * t;
                    this.y = p1.y + (p2.y - p1.y) * t;
                }

                this.progress += this.speed * 0.0035;
                if (this.progress >= 1) {
                    this.progress = 0;
                }
            }
        }

        draw(ctx) {
            ctx.fillStyle = this.color;
            ctx.shadowColor = this.color;
            ctx.shadowBlur = 5;
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fill();
            ctx.shadowBlur = 0;
        }
    }

    let mapParticles = [];
    let mapPulseOffset = 0;
    
    function initMapParticles() {
        mapParticles = [];
        const centerX = cWidth / 2;
        const centerY = cHeight / 2;
        const metroLines = getMetroLines(centerX, centerY);
        const riverPath = getRiverPath();

        // Speed modifications depending on selected state
        let speedMod = 1;
        if (activeStateKey === 'stress') speedMod = 2.4;
        else if (activeStateKey === 'apathy') speedMod = 0.4;
        else if (activeStateKey === 'chaos') speedMod = 1.8;
        else if (activeStateKey === 'balance') speedMod = 0.8;

        // Metro line particles
        metroLines.forEach(line => {
            const count = line.isRing ? 10 : 6;
            for (let i = 0; i < count; i++) {
                if (line.isRing) {
                    mapParticles.push(new SignalParticle(null, line.color, (Math.random() * 0.4 + 0.6) * speedMod, true, line));
                } else {
                    mapParticles.push(new SignalParticle(line.points, line.color, (Math.random() * 0.4 + 0.6) * speedMod));
                }
            }
        });

        // River particles
        for (let i = 0; i < 12; i++) {
            mapParticles.push(new SignalParticle(riverPath, '#38bdf8', (Math.random() * 0.3 + 0.7) * speedMod));
        }

        // Synaptic connections particles (GES-2 to others)
        const hubs = getHubNodes(centerX, centerY);
        const core = hubs[0];
        hubs.forEach((hub, idx) => {
            if (idx > 0) {
                const synPath = [
                    { x: core.x, y: core.y },
                    { x: (core.x + hub.x) / 2 + (Math.random() - 0.5) * 20, y: (core.y + hub.y) / 2 + (Math.random() - 0.5) * 20 },
                    { x: hub.x, y: hub.y }
                ];
                for (let i = 0; i < 3; i++) {
                    mapParticles.push(new SignalParticle(synPath, STATES[activeStateKey].color, (Math.random() * 0.4 + 0.8) * speedMod));
                }
            }
        });
    }

    let hoveredHub = null;
    cityCanvas.addEventListener('mousemove', (e) => {
        const rect = cityCanvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        const centerX = cWidth / 2;
        const centerY = cHeight / 2;
        const hubs = getHubNodes(centerX, centerY);
        
        hoveredHub = null;
        for (const hub of hubs) {
            const dist = Math.sqrt((hub.x - x)**2 + (hub.y - y)**2);
            if (dist < 14) {
                hoveredHub = hub;
                break;
            }
        }
    });

    function drawCityMap() {
        cCtx.fillStyle = 'rgba(2, 2, 4, 0.25)'; // trail effect
        cCtx.fillRect(0, 0, cWidth, cHeight);

        const centerX = cWidth / 2;
        const centerY = cHeight / 2;
        const stateColor = STATES[activeStateKey].color;

        // 1. Draw Ring Roads
        cCtx.strokeStyle = 'rgba(255, 255, 255, 0.02)';
        cCtx.lineWidth = 1;
        cCtx.beginPath();
        cCtx.ellipse(centerX, centerY, cWidth * 0.42, cHeight * 0.42, 0, 0, Math.PI * 2);
        cCtx.stroke();
        
        cCtx.strokeStyle = 'rgba(255, 255, 255, 0.04)';
        cCtx.beginPath();
        cCtx.ellipse(centerX, centerY, cWidth * 0.28, cHeight * 0.38, 0, 0, Math.PI * 2);
        cCtx.stroke();

        cCtx.strokeStyle = 'rgba(255, 255, 255, 0.07)';
        cCtx.beginPath();
        cCtx.ellipse(centerX, centerY, cWidth * 0.18, cHeight * 0.3, 0, 0, Math.PI * 2);
        cCtx.stroke();

        // 2. Draw Moskva River
        const riverPath = getRiverPath();
        cCtx.strokeStyle = 'rgba(14, 165, 233, 0.12)';
        cCtx.lineWidth = 8;
        cCtx.lineCap = 'round';
        cCtx.beginPath();
        riverPath.forEach((p, idx) => {
            if (idx === 0) cCtx.moveTo(p.x, p.y);
            else cCtx.lineTo(p.x, p.y);
        });
        cCtx.stroke();

        cCtx.strokeStyle = 'rgba(14, 165, 233, 0.25)';
        cCtx.lineWidth = 3;
        cCtx.stroke();

        // 3. Draw Metro Lines
        const metroLines = getMetroLines(centerX, centerY);
        metroLines.forEach(line => {
            cCtx.strokeStyle = line.color + '20';
            cCtx.lineWidth = 4;
            cCtx.beginPath();
            
            if (line.isRing) {
                cCtx.ellipse(line.centerX, line.centerY, line.radiusX, line.radiusY, 0, 0, Math.PI * 2);
            } else {
                line.points.forEach((p, idx) => {
                    if (idx === 0) cCtx.moveTo(p.x, p.y);
                    else cCtx.lineTo(p.x, p.y);
                });
            }
            cCtx.stroke();

            cCtx.strokeStyle = line.color + '40';
            cCtx.lineWidth = 1.5;
            cCtx.stroke();
        });

        // 4. Draw Synapses
        const hubs = getHubNodes(centerX, centerY);
        const core = hubs[0];
        hubs.forEach((hub, idx) => {
            if (idx > 0) {
                cCtx.strokeStyle = stateColor + '10';
                cCtx.lineWidth = 1;
                cCtx.beginPath();
                cCtx.moveTo(core.x, core.y);
                cCtx.bezierCurveTo(
                    (core.x + hub.x) / 2, core.y - 15,
                    (core.x + hub.x) / 2, hub.y + 15,
                    hub.x, hub.y
                );
                cCtx.stroke();
            }
        });

        // 5. Draw Particles
        mapParticles.forEach(p => {
            p.updatePosition();
            p.draw(cCtx);
        });

        // 6. Draw Hub Nodes
        hubs.forEach(hub => {
            const isHovered = hoveredHub && hoveredHub.id === hub.id;
            const glowMul = isHovered ? 2.2 : 1.0;
            
            cCtx.fillStyle = hub.isCore ? '#d4af37' : stateColor;
            cCtx.shadowColor = hub.isCore ? '#d4af37' : stateColor;
            cCtx.shadowBlur = (9 + Math.sin(mapPulseOffset) * 4) * glowMul;

            cCtx.beginPath();
            const r = (hub.pulseSize + Math.sin(mapPulseOffset * (hub.isCore ? 1.4 : 1.0)) * 1.2) * (isHovered ? 1.3 : 1.0);
            cCtx.arc(hub.x, hub.y, r, 0, Math.PI * 2);
            cCtx.fill();
            cCtx.shadowBlur = 0;

            cCtx.strokeStyle = hub.isCore ? 'rgba(212, 175, 55, 0.4)' : (stateColor + '55');
            cCtx.lineWidth = 1;
            cCtx.beginPath();
            cCtx.arc(hub.x, hub.y, r * (1.5 + Math.sin(mapPulseOffset * 1.1) * 0.3), 0, Math.PI * 2);
            cCtx.stroke();

            // Label
            cCtx.fillStyle = '#ffffff';
            cCtx.font = (isHovered ? 'bold 10px' : '8.5px') + ' "Outfit", sans-serif';
            cCtx.textAlign = 'center';
            cCtx.fillText(hub.name, hub.x, hub.y - r - 8);
            
            if (isHovered) {
                cCtx.fillStyle = '#94a3b8';
                cCtx.font = '8.5px monospace';
                let statusText = t.status.sync;
                if (activeStateKey === 'stress') statusText = t.status.stress;
                else if (activeStateKey === 'apathy') statusText = t.status.apathy;
                else if (activeStateKey === 'chaos') statusText = t.status.chaos;
                else if (activeStateKey === 'balance') statusText = t.status.balance;
                cCtx.fillText(statusText, hub.x, hub.y + r + 13);
            }
        });

        let pulseSpeed = 0.035;
        if (activeStateKey === 'stress') pulseSpeed = 0.07;
        else if (activeStateKey === 'apathy') pulseSpeed = 0.012;
        else if (activeStateKey === 'chaos') pulseSpeed = 0.055;
        else if (activeStateKey === 'balance') pulseSpeed = 0.03;

        mapPulseOffset += pulseSpeed;

        requestAnimationFrame(drawCityMap);
    }

    resizeCityCanvas();
    initMapParticles();
    drawCityMap();
    
    // Sync speed/colors immediately when simulator buttons are clicked
    stateButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            setTimeout(initMapParticles, 40);
        });
    });
}

