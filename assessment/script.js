const questions = [
    {
        id: 1,
        text: "What is the time complexity of binary search?",
        options: ["O(n)", "O(log n)", "O(n^2)", "O(1)"],
        answer: "O(log n)"
    },
    {
        id: 2,
        text: "Which data structure uses LIFO?",
        options: ["Queue", "Stack", "Tree", "Graph"],
        answer: "Stack"
    },
    {
        id: 3,
        text: "What does SQL stand for?",
        options: ["Structured Query Key", "Structured Query Language", "Simple Query Language", "Strong Question Language"],
        answer: "Structured Query Language"
    }
];

// Load Candidate ID from URL
const params = new URLSearchParams(window.location.search);
const candidateId = params.get('token') || "DEMO_USER";
document.getElementById('candidate-id').innerText = candidateId;

// Render Questions
const container = document.getElementById('questions-container');

questions.forEach((q, index) => {
    const qDiv = document.createElement('div');
    qDiv.className = 'question-block';

    let optionsHtml = '';
    q.options.forEach(opt => {
        optionsHtml += `
            <label>
                <input type="radio" name="q${q.id}" value="${opt}"> ${opt}
            </label>
        `;
    });

    qDiv.innerHTML = `
        <div class="question-text">${index + 1}. ${q.text}</div>
        <div class="options">${optionsHtml}</div>
    `;
    container.appendChild(qDiv);
});

function submitAssessment() {
    let score = 0;
    let answers = {};

    questions.forEach(q => {
        const selected = document.querySelector(`input[name="q${q.id}"]:checked`);
        if (selected) {
            answers[q.id] = selected.value;
            if (selected.value === q.answer) {
                score++;
            }
        }
    });

    print("test here")
    const finalScore = (score / questions.length) * 100;

    // In production, this would be a fetch() POST request to the backend
    console.log("Submitting Score:", finalScore);
    console.log("Answers:", answers);

    alert(`Assessment Submitted! Your Score: ${finalScore.toFixed(2)}% \n(In a real app, this is saved to the database)`);

    // Optional: Redirect
    // window.location.href = "thank_you.html";
}
