document.getElementById("startSession").addEventListener("click", function () {
    switchToFocus();
  
    var fiveMinutes = 15 ,
    display = document.querySelector('#timer');
    startTimer(fiveMinutes, display, switchToChill);
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
    title.innerHTML = "Chill time!"

    gradientHome.style.opacity = "0"; 
    gradientFocus.style.opacity = "0"; 
    gradientChill.style.opacity = "1"; 

    settingsPanel.style.display = "none"
    sessionPanel.style.display = "flex"

    focusBox.style.display = "none"
    chillBox.style.display = "flex"
}

function startTimer(duration, display, callback) {
    var timer = duration, minutes, seconds;
    const interval = setInterval(function () {
        minutes = parseInt(timer / 60, 10);
        seconds = parseInt(timer % 60, 10);

        minutes = minutes < 10 ? "0" + minutes : minutes;
        seconds = seconds < 10 ? "0" + seconds : seconds;

        display.textContent = minutes + ":" + seconds;

        if (--timer < 0) {
            timer = duration;
            console.log("time up")
            clearInterval(interval)
            callback()
        }
    }, 1000);
}
