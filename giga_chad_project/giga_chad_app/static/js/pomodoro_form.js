var focusTime
var restTime
var ammount
var done = 1
document.getElementById("startSession").addEventListener("click", function () {
    ammount = document.getElementById('sessionsAmmount').value
    focusTime = document.getElementById('focusTime').value
    restTime = document.getElementById('restTime').value 
    document.querySelector('#total').innerHTML = ammount
    document.querySelector('#timer').textContent = focusTime + ":00";
    document.querySelector("#focus-dot").style["animationDuration"] = 60*focusTime+"s"
    document.querySelector("#chill-dot").style["animationDuration"] = 60*restTime+"s"
    startTimer(focusTime, switchToChill);
    switchToFocus();
});

function switchToFocus() {
    const gradientHome = document.querySelector(".gradient-home");
    const gradientFocus = document.querySelector(".gradient-focus");
    const gradientChill = document.querySelector(".gradient-chill");
    
    const settingsPanel = document.querySelector("#settings-panel");
    const sessionPanel = document.querySelector("#session-panel");

    const chillBox = document.querySelector("#chill-box");
    const focusBox = document.querySelector("#focus-box");
    const title = document.querySelector("#session-title");
    title.innerHTML = "Focus Session"
    
    gradientHome.style.opacity = "0"; 
    gradientFocus.style.opacity = "1"; 
    gradientChill.style.opacity = "0"; 
    
    settingsPanel.style.display = "none"
    sessionPanel.style.display = "flex"
    
    focusBox.style.display = "flex"
    chillBox.style.display = "none"
    startTimer(focusTime, switchToChill);
}

function switchToChill() {
    const gradientHome = document.querySelector(".gradient-home");
    const gradientFocus = document.querySelector(".gradient-focus");
    const gradientChill = document.querySelector(".gradient-chill");

    const settingsPanel = document.querySelector("#settings-panel");
    const sessionPanel = document.querySelector("#session-panel");
    const chillBox = document.querySelector("#chill-box");
    const focusBox = document.querySelector("#focus-box");
    const title = document.querySelector("#session-title");
    title.innerHTML = "Rest Period"

    gradientHome.style.opacity = "0"; 
    gradientFocus.style.opacity = "0"; 
    gradientChill.style.opacity = "1"; 

    settingsPanel.style.display = "none"
    sessionPanel.style.display = "flex"

    focusBox.style.display = "none"
    chillBox.style.display = "flex"
    startTimer(focusTime, switchToFocus);
}

function startTimer(duration,  callback) {
    duration *= 60
    var timer = duration, minutes, seconds;
    const interval = setInterval(function () {
        minutes = parseInt(timer / 60, 10);
        seconds = parseInt(timer % 60, 10);

        minutes = minutes < 10 ? "0" + minutes : minutes;
        seconds = seconds < 10 ? "0" + seconds : seconds;

        document.querySelector('#timer').textContent = minutes + ":" + seconds;

        if (--timer < 0) {
            timer = duration;
            console.log("time up")
            clearInterval(interval)
            callback()
        }
    }, 1000);
}
