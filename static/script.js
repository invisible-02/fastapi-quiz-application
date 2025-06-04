// State management
let currentUser = null;
let currentQuestions = [];
let currentQuestionIndex = 0;
let userAnswers = {};
let accessToken = null;

// DOM Elements
const authSection = document.getElementById('authSection');
const quizSection = document.getElementById('quizSection');
const loginForm = document.getElementById('loginForm');
const registerForm = document.getElementById('registerForm');
const loginTab = document.getElementById('loginTab');
const registerTab = document.getElementById('registerTab');
const startQuizBtn = document.getElementById('startQuizBtn');
const nextQuestionBtn = document.getElementById('nextQuestionBtn');
const logoutBtn = document.getElementById('logoutBtn');
const questionText = document.getElementById('questionText');
const progressBar = document.getElementById('progressBar');
const progressText = document.getElementById('progressText');
const messageToast = document.getElementById('messageToast');
const messageText = document.getElementById('messageText');

// Event Listeners
loginTab.addEventListener('click', () => switchForm('login'));
registerTab.addEventListener('click', () => switchForm('register'));
loginForm.addEventListener('submit', handleLogin);
registerForm.addEventListener('submit', handleRegister);
startQuizBtn.addEventListener('click', startQuiz);
nextQuestionBtn.addEventListener('click', showNextQuestion);
logoutBtn.addEventListener('click', handleLogout);

document.querySelectorAll('.option-btn').forEach(button => {
    button.addEventListener('click', () => handleAnswerSelection(button));
});

// Form switching
function switchForm(form) {
    if (form === 'login') {
        loginForm.classList.remove('hidden');
        registerForm.classList.add('hidden');
        loginTab.classList.add('border-blue-500', 'text-blue-500');
        loginTab.classList.remove('border-gray-200', 'text-gray-500');
        registerTab.classList.add('border-gray-200', 'text-gray-500');
        registerTab.classList.remove('border-blue-500', 'text-blue-500');
    } else {
        loginForm.classList.add('hidden');
        registerForm.classList.remove('hidden');
        registerTab.classList.add('border-blue-500', 'text-blue-500');
        registerTab.classList.remove('border-gray-200', 'text-gray-500');
        loginTab.classList.add('border-gray-200', 'text-gray-500');
        loginTab.classList.remove('border-blue-500', 'text-blue-500');
    }
}

// Toast message
function showMessage(message, isError = false) {
    messageText.textContent = message;
    messageToast.classList.remove('bg-gray-800', 'bg-red-500');
    messageToast.classList.add(isError ? 'bg-red-500' : 'bg-gray-800');
    messageToast.classList.add('toast-show');

    setTimeout(() => {
        messageToast.classList.remove('toast-show');
        messageToast.classList.add('toast-hide');
    }, 3000);
}

// Authentication handlers
async function handleLogin(e) {
    e.preventDefault();
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;

    try {
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        const response = await fetch('/token', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            accessToken = data.access_token;
            currentUser = username;
            showQuizSection();
            showMessage('Successfully logged in!');
        } else {
            showMessage(data.detail || 'Login failed', true);
        }
    } catch (error) {
        showMessage('An error occurred during login', true);
    }
}

async function handleRegister(e) {
    e.preventDefault();
    const username = document.getElementById('registerUsername').value;
    const password = document.getElementById('registerPassword').value;

    try {
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        const response = await fetch('/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            showMessage('Registration successful! Please login.');
            switchForm('login');
        } else {
            showMessage(data.detail || 'Registration failed', true);
        }
    } catch (error) {
        showMessage('An error occurred during registration', true);
    }
}

function handleLogout() {
    accessToken = null;
    currentUser = null;
    currentQuestions = [];
    currentQuestionIndex = 0;
    userAnswers = {};
    showAuthSection();
    showMessage('Successfully logged out!');
}

// Quiz functionality
async function startQuiz() {
    try {
        const response = await fetch('/start', {
            headers: {
                'Authorization': `Bearer ${accessToken}`
            }
        });

        const data = await response.json();

        if (response.ok) {
            currentQuestions = data.questions;
            currentQuestionIndex = 0;
            userAnswers = {};
            updateProgress();
            showQuestion();
            startQuizBtn.classList.add('hidden');
            nextQuestionBtn.classList.remove('hidden');
            showMessage('Quiz started!');
        } else {
            showMessage(data.detail || 'Failed to start quiz', true);
        }
    } catch (error) {
        showMessage('An error occurred while starting the quiz', true);
    }
}

function showQuestion() {
    if (currentQuestionIndex >= currentQuestions.length) {
        showMessage('Quiz completed!');
        questionText.textContent = 'Quiz completed!';
        nextQuestionBtn.classList.add('hidden');
        startQuizBtn.classList.remove('hidden');
        startQuizBtn.textContent = 'Start New Quiz';
        return;
    }

    const question = currentQuestions[currentQuestionIndex];
    questionText.textContent = question.question_text;

    // Reset option selection
    document.querySelectorAll('.option-btn').forEach(btn => {
        btn.classList.remove('selected');
        if (userAnswers[question.id] === btn.dataset.value) {
            btn.classList.add('selected');
        }
    });
}

async function handleAnswerSelection(button) {
    const question = currentQuestions[currentQuestionIndex];
    const answer = button.dataset.value;

    try {
        const response = await fetch('/answer', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                question_id: question.id,
                answer: answer
            })
        });

        if (response.ok) {
            userAnswers[question.id] = answer;
            document.querySelectorAll('.option-btn').forEach(btn => {
                btn.classList.remove('selected');
            });
            button.classList.add('selected');
            updateProgress();
            showMessage('Answer saved!');
        } else {
            const data = await response.json();
            showMessage(data.detail || 'Failed to save answer', true);
        }
    } catch (error) {
        showMessage('An error occurred while saving the answer', true);
    }
}

function showNextQuestion() {
    if (currentQuestionIndex < currentQuestions.length - 1) {
        currentQuestionIndex++;
        showQuestion();
    } else {
        showMessage('Quiz completed!');
        nextQuestionBtn.classList.add('hidden');
        startQuizBtn.classList.remove('hidden');
        startQuizBtn.textContent = 'Start New Quiz';
    }
}

async function updateProgress() {
    try {
        const response = await fetch('/progress', {
            headers: {
                'Authorization': `Bearer ${accessToken}`
            }
        });

        const data = await response.json();

        if (response.ok) {
            const percentage = data.percentage || 0;
            progressBar.style.width = `${percentage}%`;
            progressText.textContent = `${data.progress} of ${data.total_questions} questions answered`;
        }
    } catch (error) {
        console.error('Error updating progress:', error);
    }
}

// Section visibility
function showQuizSection() {
    authSection.classList.add('hidden');
    quizSection.classList.remove('hidden');
}

function showAuthSection() {
    authSection.classList.remove('hidden');
    quizSection.classList.add('hidden');
}

const adminSecretKey = "FirstApplication@iitmz"; // Replace with your actual secret key

// Check for existing session
const savedToken = localStorage.getItem('accessToken');
if (savedToken) {
    accessToken = savedToken;
    showQuizSection();
    updateProgress();
}

// Admin Download Section Elements
const adminDownloadSection = document.getElementById('adminDownloadSection');
const adminSecretKeyInput = document.getElementById('adminSecretKey');
const adminDownloadBtn = document.getElementById('adminDownloadBtn');
const adminDownloadMessage = document.getElementById('adminDownloadMessage');

// Function to show admin download section if secret key matches
function showAdminDownloadSection() {
    adminDownloadSection.classList.remove('hidden');
}

// Function to hide admin download section
function hideAdminDownloadSection() {
    adminDownloadSection.classList.add('hidden');
    adminDownloadMessage.classList.add('hidden');
    adminSecretKeyInput.value = '';
}

// Event listener for admin download button
adminDownloadBtn.addEventListener('click', async () => {
    const enteredKey = adminSecretKeyInput.value.trim();
    if (enteredKey !== adminSecretKey) {
        adminDownloadMessage.textContent = 'Invalid secret key.';
        adminDownloadMessage.classList.remove('hidden');
        return;
    }
    adminDownloadMessage.classList.add('hidden');

    try {
        // Fetch complete data download endpoint
        const response = await fetch('/data/complete-download', {
            headers: {
                'Authorization': `Bearer ${accessToken}`
            }
        });

        if (!response.ok) {
            adminDownloadMessage.textContent = 'Failed to download data.';
            adminDownloadMessage.classList.remove('hidden');
            return;
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'complete_quiz_data.json';
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
        adminDownloadMessage.textContent = 'Download started.';
        adminDownloadMessage.classList.remove('hidden');
    } catch (error) {
        adminDownloadMessage.textContent = 'An error occurred during download.';
        adminDownloadMessage.classList.remove('hidden');
    }
});

function showAdminDownloadSection() {
    adminDownloadSection.classList.remove('hidden');
}

function hideAdminDownloadSection() {
    adminDownloadSection.classList.add('hidden');
    adminDownloadMessage.classList.add('hidden');
    adminSecretKeyInput.value = '';
}

const adminUsername = "admin"; // Predefined admin username
const adminPassword = "admin123"; // Predefined admin password

// Admin Login Section Elements
const adminLoginSection = document.getElementById('adminLoginSection');
const adminLoginForm = document.getElementById('adminLoginForm');
const adminUsernameInput = document.getElementById('adminUsername');
const adminPasswordInput = document.getElementById('adminPassword');
const adminLoginMessage = document.getElementById('adminLoginMessage');

// Admin Download Section Elements
const adminDownloadSection = document.getElementById('adminDownloadSection');
const adminDownloadBtn = document.getElementById('adminDownloadBtn');
const adminDownloadMessage = document.getElementById('adminDownloadMessage');

// Show admin login section only if user is logged in and quiz section is visible
function showAdminLoginSection() {
    adminLoginSection.classList.remove('hidden');
}

function hideAdminLoginSection() {
    adminLoginSection.classList.add('hidden');
    adminLoginMessage.classList.add('hidden');
    adminUsernameInput.value = '';
    adminPasswordInput.value = '';
}

// Show admin download section
function showAdminDownloadSection() {
    adminDownloadSection.classList.remove('hidden');
}

// Hide admin download section
function hideAdminDownloadSection() {
    adminDownloadSection.classList.add('hidden');
    adminDownloadMessage.classList.add('hidden');
}

// Admin login form submit handler
adminLoginForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const enteredUsername = adminUsernameInput.value.trim();
    const enteredPassword = adminPasswordInput.value.trim();

    if (enteredUsername === adminUsername && enteredPassword === adminPassword) {
        hideAdminLoginSection();
        showAdminDownloadSection();
    } else {
        adminLoginMessage.textContent = 'Invalid admin credentials.';
        adminLoginMessage.classList.remove('hidden');
    }
});

// Event listener for admin download button
adminDownloadBtn.addEventListener('click', async () => {
    try {
        // Fetch complete data download endpoint
        const response = await fetch('/data/complete-download', {
            headers: {
                'Authorization': `Bearer ${accessToken}`
            }
        });

        if (!response.ok) {
            adminDownloadMessage.textContent = 'Failed to download data.';
            adminDownloadMessage.classList.remove('hidden');
            return;
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'complete_quiz_data.json';
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
        adminDownloadMessage.textContent = 'Download started.';
        adminDownloadMessage.classList.remove('hidden');
    } catch (error) {
        adminDownloadMessage.textContent = 'An error occurred during download.';
        adminDownloadMessage.classList.remove('hidden');
    }
});

// Show admin login section only if user is logged in and quiz section is visible
if (accessToken && !authSection.classList.contains('hidden')) {
    showAdminLoginSection();
    hideAdminDownloadSection();
} else {
    hideAdminLoginSection();
    hideAdminDownloadSection();
}
