// ATS Resume Analyzer - JavaScript Application

// Update time display
function updateTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('en-US');
    document.getElementById('timeDisplay').textContent = `Updated: ${timeString}`;
}

updateTime();
setInterval(updateTime, 1000);

// Demo mode functionality
let demoMode = true;

// Animate stats on page load
window.addEventListener('load', () => {
    if (demoMode) {
        animateStats();
    }
});

function animateStats() {
    // Animate counter values
    animateValue('totalResumes', 0, 1247, 2000);
    animateValue('analyzedCandidates', 0, 983, 2000);
    animateValue('avgMatchScore', 0, 78, 2000, '%');
    
    // Animate processing time differently
    setTimeout(() => {
        document.getElementById('avgProcessingTime').textContent = '2.3 days';
    }, 1000);
}

function animateValue(id, start, end, duration, suffix = '') {
    const element = document.getElementById(id);
    const range = end - start;
    const increment = range / (duration / 16);
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        if (current >= end) {
            current = end;
            clearInterval(timer);
        }
        element.textContent = Math.floor(current) + suffix;
    }, 16);
}

// File upload handling
const uploadBox = document.getElementById('uploadBox');
const fileInput = document.getElementById('fileInput');
const analyzeBtn = document.getElementById('analyzeBtn');
let selectedFile = null;

// Drag and drop
uploadBox.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadBox.style.borderColor = '#667eea';
    uploadBox.style.background = 'linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%)';
});

uploadBox.addEventListener('dragleave', () => {
    uploadBox.style.borderColor = '#e5e7eb';
    uploadBox.style.background = 'transparent';
});

uploadBox.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadBox.style.borderColor = '#e5e7eb';
    uploadBox.style.background = 'transparent';
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
});

// File input change
fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFile(e.target.files[0]);
    }
});

function handleFile(file) {
    // Validate file type
    const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
    
    if (!allowedTypes.includes(file.type) && !file.name.match(/\.(pdf|docx|txt)$/i)) {
        alert('Please upload a PDF, DOCX, or TXT file');
        return;
    }
    
    // Validate file size (10MB max)
    if (file.size > 10 * 1024 * 1024) {
        alert('File size must be less than 10MB');
        return;
    }
    
    selectedFile = file;
    
    // Update UI
    uploadBox.innerHTML = `
        <div class="upload-icon">✓</div>
        <h3 class="upload-title">${file.name}</h3>
        <p class="upload-text">${(file.size / 1024).toFixed(2)} KB</p>
        <button class="btn-primary" onclick="document.getElementById('fileInput').click()">
            Change File
        </button>
    `;
    
    // Enable analyze button
    analyzeBtn.disabled = false;
}

// Analyze button click
analyzeBtn.addEventListener('click', async () => {
    if (!selectedFile) {
        alert('Please select a file first');
        return;
    }
    
    // Show loading state
    analyzeBtn.innerHTML = '<span class="btn-icon">⏳</span> Analyzing...';
    analyzeBtn.disabled = true;
    
    if (demoMode) {
        // Demo mode: Show mock results after delay
        setTimeout(() => {
            showDemoResults();
            analyzeBtn.innerHTML = '<span class="btn-icon">🔍</span> Analyze Resume';
            analyzeBtn.disabled = false;
        }, 2000);
    } else {
        // Real mode: Call API
        await analyzeResumeAPI();
    }
});

async function analyzeResumeAPI() {
    const formData = new FormData();
    formData.append('file', selectedFile);
    
    const jobDescription = document.getElementById('jobDescription').value;
    const requiredSkills = document.getElementById('requiredSkills').value;
    
    if (jobDescription) formData.append('job_description', jobDescription);
    if (requiredSkills) formData.append('required_skills', requiredSkills);
    
    try {
        const response = await fetch('/api/analyze-resume', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('Analysis failed');
        }
        
        const data = await response.json();
        showResults(data);
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to analyze resume. Please try again.');
    } finally {
        analyzeBtn.innerHTML = '<span class="btn-icon">🔍</span> Analyze Resume';
        analyzeBtn.disabled = false;
    }
}

function showDemoResults() {
    const mockData = {
        ats_score: {
            overall_score: 82.5,
            grade: 'B',
            section_scores: {
                formatting: 85,
                keywords: 78,
                experience: 90,
                education: 80,
                skills: 82
            },
            strengths: [
                'Formatting: Excellent',
                'Experience: Excellent',
                'Skills: Excellent'
            ],
            weaknesses: [
                'Keywords: Needs improvement'
            ],
            recommendations: [
                'Include these important keywords: Machine Learning, Cloud Computing',
                'Add quantifiable achievements (e.g., "Increased sales by 30%")',
                'Use strong action verbs (e.g., developed, managed, implemented)',
                'Consider adding more relevant skills (aim for 8-15 skills)'
            ]
        },
        skills: {
            extracted: [
                { skill: 'Python', category: 'Programming Languages', weight: 0.9 },
                { skill: 'JavaScript', category: 'Programming Languages', weight: 0.85 },
                { skill: 'React', category: 'Web Development', weight: 0.9 },
                { skill: 'Node.js', category: 'Web Development', weight: 0.9 },
                { skill: 'AWS', category: 'Cloud & DevOps', weight: 0.95 },
                { skill: 'Docker', category: 'Cloud & DevOps', weight: 0.9 },
                { skill: 'SQL', category: 'Database', weight: 0.9 },
                { skill: 'Git', category: 'Tools & Frameworks', weight: 0.85 }
            ]
        }
    };
    
    showResults(mockData);
}

function showResults(data) {
    // Show results section
    const resultsSection = document.getElementById('resultsSection');
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    
    // Update ATS score
    const score = data.ats_score.overall_score;
    const grade = data.ats_score.grade;
    
    document.getElementById('scoreGrade').textContent = grade;
    document.getElementById('scoreText').textContent = Math.round(score);
    
    // Animate score circle
    const circle = document.getElementById('scoreCircle');
    const circumference = 2 * Math.PI * 90;
    const offset = circumference - (score / 100) * circumference;
    
    setTimeout(() => {
        circle.style.transition = 'stroke-dashoffset 1.5s ease';
        circle.style.strokeDashoffset = offset;
    }, 100);
    
    // Update section scores
    updateSectionScore('formatScore', 'formatValue', data.ats_score.section_scores.formatting);
    updateSectionScore('keywordScore', 'keywordValue', data.ats_score.section_scores.keywords);
    updateSectionScore('experienceScore', 'experienceValue', data.ats_score.section_scores.experience);
    updateSectionScore('educationScore', 'educationValue', data.ats_score.section_scores.education);
    updateSectionScore('skillsScore', 'skillsValue', data.ats_score.section_scores.skills);
    
    // Update skills
    const skillsContainer = document.getElementById('skillsContainer');
    skillsContainer.innerHTML = '';
    
    data.skills.extracted.forEach(skill => {
        const badge = document.createElement('span');
        badge.className = 'skill-badge';
        badge.textContent = skill.skill;
        skillsContainer.appendChild(badge);
    });
    
    // Update recommendations
    const recommendationsList = document.getElementById('recommendationsList');
    recommendationsList.innerHTML = '';
    
    data.ats_score.recommendations.forEach(rec => {
        const item = document.createElement('div');
        item.className = 'recommendation-item';
        item.innerHTML = `
            <span class="recommendation-icon">💡</span>
            <span>${rec}</span>
        `;
        recommendationsList.appendChild(item);
    });
    
    // Initialize charts
    initializeCharts();
}

function updateSectionScore(barId, valueId, score) {
    const bar = document.getElementById(barId);
    const value = document.getElementById(valueId);
    
    setTimeout(() => {
        bar.style.width = `${score}%`;
        value.textContent = `${Math.round(score)}%`;
    }, 300);
}

// Chart initialization
function initializeCharts() {

    
    // Skills Chart
    const skillsCtx = document.getElementById('skillsChart');
    if (skillsCtx && !skillsCtx.chart) {
        drawSkillsChart(skillsCtx);
    }
}

function drawMonthlyChart(canvas) {
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    
    // Mock data
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const data = [45, 52, 38, 65, 70, 58, 72, 68, 75, 82, 90, 95];
    
    const max = Math.max(...data);
    const padding = 40;
    const graphWidth = width - padding * 2;
    const graphHeight = height - padding * 2;
    
    // Clear canvas
    ctx.clearRect(0, 0, width, height);
    
    // Draw grid lines
    ctx.strokeStyle = '#f0f0f0';
    ctx.lineWidth = 1;
    
    for (let i = 0; i <= 5; i++) {
        const y = padding + (graphHeight / 5) * i;
        ctx.beginPath();
        ctx.moveTo(padding, y);
        ctx.lineTo(width - padding, y);
        ctx.stroke();
    }
    
    // Draw line
    const gradient = ctx.createLinearGradient(0, 0, width, 0);
    gradient.addColorStop(0, '#667eea');
    gradient.addColorStop(1, '#764ba2');
    
    ctx.strokeStyle = gradient;
    ctx.lineWidth = 3;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    
    ctx.beginPath();
    
    data.forEach((value, index) => {
        const x = padding + (graphWidth / (data.length - 1)) * index;
        const y = height - padding - (value / max) * graphHeight;
        
        if (index === 0) {
            ctx.moveTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
    });
    
    ctx.stroke();
    
    // Draw points
    data.forEach((value, index) => {
        const x = padding + (graphWidth / (data.length - 1)) * index;
        const y = height - padding - (value / max) * graphHeight;
        
        ctx.fillStyle = '#667eea';
        ctx.beginPath();
        ctx.arc(x, y, 5, 0, Math.PI * 2);
        ctx.fill();
        
        // Draw labels
        ctx.fillStyle = '#9ca3af';
        ctx.font = '12px Outfit';
        ctx.textAlign = 'center';
        ctx.fillText(months[index], x, height - padding + 20);
    });
    
    canvas.chart = true;
}

function drawSkillsChart(canvas) {
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    
    // Mock data
    const skills = ['Python', 'JavaScript', 'React', 'AWS', 'Docker'];
    const data = [95, 88, 82, 78, 70];
    
    const barHeight = 40;
    const padding = 60;
    const maxBarWidth = width - padding * 2;
    const max = 100;
    
    // Clear canvas
    ctx.clearRect(0, 0, width, height);
    
    // Draw bars
    data.forEach((value, index) => {
        const y = padding + index * (barHeight + 20);
        const barWidth = (value / max) * maxBarWidth;
        
        // Background bar
        ctx.fillStyle = '#f3f4f8';
        ctx.fillRect(padding, y, maxBarWidth, barHeight);
        
        // Value bar with gradient
        const gradient = ctx.createLinearGradient(padding, y, padding + barWidth, y);
        gradient.addColorStop(0, '#667eea');
        gradient.addColorStop(1, '#764ba2');
        
        ctx.fillStyle = gradient;
        ctx.fillRect(padding, y, barWidth, barHeight);
        
        // Skill label
        ctx.fillStyle = '#1a1d2e';
        ctx.font = '14px Outfit';
        ctx.textAlign = 'right';
        ctx.fillText(skills[index], padding - 10, y + barHeight / 2 + 5);
        
        // Value label
        ctx.fillStyle = '#ffffff';
        ctx.textAlign = 'left';
        ctx.fillText(value + '%', padding + barWidth - 40, y + barHeight / 2 + 5);
    });
    
    canvas.chart = true;
}

// Setup guide button
document.getElementById('setupGuideBtn').addEventListener('click', () => {
    alert('Setup Guide\n\n1. Install Python dependencies: pip install -r requirements.txt\n2. Configure your database connection\n3. Run the application: python api/main.py\n4. Visit http://localhost:8000\n\nFor more details, check the README.md file.');
});

// Download report button
document.getElementById('downloadReportBtn').addEventListener('click', () => {
    alert('Report download feature coming soon!');
});

// Initialize charts on page load
window.addEventListener('load', () => {
    setTimeout(initializeCharts, 1000);
});

// Handle navigation
document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', (e) => {
        e.preventDefault();
        document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
        item.classList.add('active');
    });
});

console.log('🚀 ATS Resume Analyzer loaded successfully!');
console.log('📊 Demo Mode: ' + (demoMode ? 'ACTIVE' : 'INACTIVE'));