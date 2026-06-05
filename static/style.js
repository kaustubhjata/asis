// Wait for the DOM to load before running the script
document.addEventListener("DOMContentLoaded", () => {
    // Add animations to the header
    const header = document.querySelector("header");
    header.classList.add("slide-in");

    // Add hover effects to the navigation links
    const navLinks = document.querySelectorAll("nav ul li a");
    navLinks.forEach(link => {
        link.addEventListener("mouseover", () => {
            link.style.color = "#2e7d32";
        });
        link.addEventListener("mouseout", () => {
            link.style.color = "#4caf50";
        });
    });

    // Button animations for feature cards
    const featureButtons = document.querySelectorAll(".feature-card .btn");
    featureButtons.forEach(button => {
        button.addEventListener("click", () => {
            button.classList.add("clicked");
            setTimeout(() => {
                button.classList.remove("clicked");
            }, 300);
        });
    });

    // Smooth scroll functionality for navigation links
    navLinks.forEach(link => {
        link.addEventListener("click", event => {
            event.preventDefault();
            const targetId = link.getAttribute("href").substring(1);
            const targetSection = document.getElementById(targetId);
            if (targetSection) {
                window.scrollTo({
                    top: targetSection.offsetTop,
                    behavior: "smooth"
                });
            }
        });
    });


    // Handle the stop speech functionality
stopSpeechBtn.addEventListener('click', () => {
    fetch('/stop_speech', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log(data.status); // Log the response from the server
    })
    .catch(error => console.error('Error:', error));
});

    // Fade-in animation for feature cards
    const featureCards = document.querySelectorAll(".feature-card");
    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add("fade-in");
            }
        });
    }, { threshold: 0.5 });

    featureCards.forEach(card => observer.observe(card));

    // Voice-to-Text functionality
    const startBtn = document.getElementById("start-recording");
    const stopBtn = document.getElementById("stop-recording");
    const transcriptionArea = document.getElementById("transcription-area");

    if (startBtn && stopBtn && transcriptionArea) {
        startBtn.addEventListener('click', () => {
            // Disable the start button and enable the stop button
            startBtn.disabled = true;
            stopBtn.disabled = false;
        
            // Change the microphone icon color and update the status text
            micIcon.classList.add('text-yellow-500'); // Yellow for 5-second countdown
            statusText.textContent = 'Preparing to Record...';
        
            // Start a 5-second timer
            setTimeout(() => {
                fetch('/voice_to_text', {
                    method: 'POST',
                    body: new URLSearchParams({ 'action': 'start' })
                });
        
                // Update the status after the timer ends
                micIcon.classList.add('text-green-500'); // Green for recording
                statusText.textContent = 'Recording in Progress';
            }, 5000); // 5000 milliseconds = 5 seconds
        });
        
    }
});
