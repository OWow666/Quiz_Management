// scripts.js
// 获取题目数据
async function fetchQuestions(mode) {
    let url = mode === 'wrong' ? '/get_wrong_questions/' : '/get_questions/';

    const response = await fetch(url);
    if (!response.ok) throw new Error('Network response was not ok');
    return response.json();
}

// 保存错误题
async function saveWrongQuestion(questionId) {
    const response = await fetch('/save_wrong_question/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            question_id: questionId
        })
    });
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
}

// 获取Cookie中的CSRF Token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// 当前题目
let currentQuestion = null;
// 当前模式（general 或 wrong）
let currentMode = null;
// 用户选择的答案
let userAnswer = null;

function not_login_wrong() {
    alert("请登录后使用错题集功能")
}

// 开始刷题
function startQuiz(mode) {
    currentMode = mode;
    document.getElementById('menu').style.display = 'none';
    document.getElementById('quiz-container').style.display = 'block';
    document.getElementById('feedback').classList.add('hidden');
    document.getElementById('next-btn').disabled = true;

    loadQuestion();
}



function parseOptions(optionsStr) {
    // Improved option parsing that handles Excel format
    if (!optionsStr) return [];

    // Split options by the pattern "A. ", "B. ", etc.
    const options = [];
    const optionPattern = /([A-D])[．\.]\s*(.*?)(?=\s+[A-D][．\.]|$)/g;
    let match;

    while ((match = optionPattern.exec(optionsStr)) !== null) {
        options.push(match[2].trim());
    }

    return options.length > 0 ? options : optionsStr.split(/\s+/).filter(Boolean);
}


let shownQuestionIds = [];


// 加载题目
async function loadQuestion() {
    let questions = [];
    const response = await fetchQuestions(currentMode);
    const data = await response;

    // Filter questions based on mode
    if (currentMode === 'general') {
        questions = data.questions.filter(q =>
            !shownQuestionIds.includes(q.id)
        );
    } else {
        questions = data.questions;
    }

    if (questions.length === 0) {
        document.getElementById('question').textContent = currentMode === 'wrong' ? '暂无错误题' : '暂无题目';
        document.getElementById('options').innerHTML = '';
        return;
    }

    // 随机选择一个题目
    const randomIndex = Math.floor(Math.random() * questions.length);
    currentQuestion = questions[randomIndex].fields;
    userAnswer = null;

    // 记录已出现的问题


    // 显示题目
    document.getElementById('question').textContent = currentQuestion.content;

    // 显示选项
    const optionsContainer = document.getElementById('options');
    optionsContainer.innerHTML = '';

    if (currentQuestion.type === '判断题') {
        const options = ["对", "错"];
        options.forEach((option, index) => {
            const button = document.createElement('button');
            button.textContent = option;
            button.className = 'option-button';
            button.onclick = function() {
                selectOption(button, index === 0 ? '正确' : '错误');
            };
            optionsContainer.appendChild(button);
        });
    } else if (currentQuestion.type === '单选题') {
        // 解析选项字符串
        const options = parseOptions(currentQuestion.options);

        options.forEach((option, index) => {
            if (option) { // 确保选项不为空字符串
                const button = document.createElement('button');
                button.textContent = `${String.fromCharCode(65 + index)}. ${option}`;
                button.className = 'option-button';
                button.onclick = function() {
                    selectOption(button, String.fromCharCode(65 + index));
                };
                optionsContainer.appendChild(button);
            }
        });
    }
}

// 选择选项
function selectOption(button, answer) {
    userAnswer = answer;

    // 移除所有选项的选中样式
    const optionButtons = document.querySelectorAll('.option-button');
    optionButtons.forEach(btn => btn.classList.remove('selected'));

    // 添加选中样式到当前选项
    button.classList.add('selected');
}

function isLoggedIn() {
    // 尝试获取用户信息元素
    const userElement = document.querySelector('a[href*="logout"]');
    return userElement !== null;
}


async function clearUserData() {
    if (!confirm('确定要重置所有题目进度吗？此操作不可撤销！')) return;

    try {
        const response = await fetch('/clear_data/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            credentials: 'same-origin'
        });

        const result = await response.json();
        alert(result.message);
        if (response.ok) location.reload(); // Refresh to reflect changes
    } catch (error) {
        console.error('清除错误:', error);
        alert('清除失败: ' + error.message);
    }
}
document.getElementById('clear-btn').addEventListener('click', clearUserData);

// 提交答案
async function submitAnswer() {
    if (userAnswer === null) {
        alert('请选择一个选项后再提交！');
        return;
    }

    const feedbackElement = document.getElementById('feedback');
    feedbackElement.classList.remove('hidden');

    // 判断是否回答正确
    const isCorrect = userAnswer === currentQuestion.answer;
    if (isCorrect) {
        feedbackElement.textContent = `回答正确！`;
        feedbackElement.className = 'feedback correct';
    } else {
        feedbackElement.textContent = `回答错误！正确答案是：${currentQuestion.answer}`;
        feedbackElement.className = 'feedback incorrect';
    }


    if (currentMode === 'general') {
        shownQuestionIds.push(currentQuestion.id);

        if (!isCorrect && isLoggedIn()) {
            await saveWrongQuestion(currentQuestion.id);
        }
    }
    await fetch('/record_attempt/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            question_id: currentQuestion.id,
            is_correct: isCorrect
        })
    });
    // feedbackElement.textContent = `1`;
    // 禁用提交按钮，启用下一题按钮
    document.querySelector('.submit-button').disabled = true;
    document.getElementById('next-btn').disabled = false;
}

// 下一题
function nextQuestion() {
    // 重置界面
    document.getElementById('feedback').classList.add('hidden');
    document.querySelector('.submit-button').disabled = false;
    document.getElementById('next-btn').disabled = true;

    // 移除所有选项的选中样式
    const optionButtons = document.querySelectorAll('.option-button');
    optionButtons.forEach(btn => btn.classList.remove('selected'));

    // 加载下一题
    loadQuestion();
}

// 结束刷题
function endQuiz() {
    document.getElementById('quiz-container').style.display = 'none';
    document.getElementById('menu').style.display = 'block';
}