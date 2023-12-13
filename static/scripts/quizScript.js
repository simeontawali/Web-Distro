const questions = [
    {
        question: "How strong do you like your coffee to be?",
        answers: [
            {text: "Very Strong", value: 4},
            {text: "Strong", value: 3},
            {text: "Mild", value: 2},
            {text: "Weak", value: 1},
        ]
    },
    {
        question: "How black do you like your coffee?",
        answers: [
            {text: "Just Black", value: 4},
            {text: "With some creamer", value: 3},
            {text: "Very Light with creamer", value: 2},
            {text: "With lots of added flavor", value: 1},
        ]
    },
    {
        question: "What style of coffee is your favorite?",
        answers: [
            {text: "Simple Coffee", value: 4},
            {text: "Latte Style", value: 3},
            {text: "Frappuccino", value: 2},
            {text: "Iced Coffee", value: 1},
        ]
    },
    {
        question: "What kind of creamer do you like with your coffee?",
        answers: [
            {text: "Whole Cream", value: 4},
            {text: "Half and Half", value: 3},
            {text: "Simple Flavors", value: 2},
            {text: "Sweetened Flavors", value: 1},
        ]
    }
];

const questionElement = document.getElementById("question");
const answerButtons = document.getElementById("answer-buttons");
const nextButton = document.getElementById("next-btn");
const finishButton = document.getElementById("finish-btn");

let currentQuestionIndex = 0;
let score = 0;

function startQuiz(){
    currentQuestionIndex = 0;
    score = 0;
    nextButton.innerHTML = "Next";
    showQuestion();
}

function showQuestion(){
    resetState();
    let currentQuestion = questions[currentQuestionIndex];
    let questionNo = currentQuestionIndex + 1;
    questionElement.innerHTML = questionNo + ". " + currentQuestion.question;

    currentQuestion.answers.forEach(answer => {
        const button = document.createElement("button");
        button.innerHTML = answer.text;
        button.classList.add("btn");
        answerButtons.appendChild(button);
        if(answer.value){
            button.dataset.value = answer.value;
        }
        button.addEventListener("click", selectAnswer);
    });
}

function resetState(){
    nextButton.style.diplay = "none"
    while(answerButtons.firstChild){
        answerButtons.removeChild(answerButtons.firstChild);
    }
}

function selectAnswer(e){
    const selectedBtn = e.target;
    score = score + selectedBtn.dataset.value;
    console.log(score);
    Array.from(answerButtons.children).forEach(button=>{
        button.disabled = true;
    });
    nextButton.style.display = "block";
}

function showScore(){
    resetState();
    questionElement.innerHTML = `Your personalized coffee taste number is ${score}`;
    nextButton.style.display = "block";
    finishButton.style.disply = "block";
    finishButton.addEventListener("click", window.location = '/home');
}

function handleNextButton(){
    currentQuestionIndex++;
    if(currentQuestionIndex < questions.length){
        showQuestion();
    }else{
        showScore();
    }
}

nextButton.addEventListener("click", ()=>{
    if(currentQuestionIndex < questions.length){
        handleNextButton();
    }else{
        startQuiz();
    }
});

startQuiz();