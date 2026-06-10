// ASK AI FUNCTION

async function askAI() {

    const question =
        document.getElementById("question").value.trim();

    const responseBox =
        document.getElementById("aiResponse");

    if (question === "") {

        responseBox.innerHTML =
            "⚠️ Please enter a question first.";

        return;
    }

    responseBox.innerHTML =
        "⏳ Generating response...";

    try {

        const response =
            await fetch("/ask-ai", {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({

                    question: question,

                    scheme_name:
                        document.getElementById("schemeName").innerText,

                    benefits:
                        document.getElementById("schemeBenefits").innerText

                })

            });

        const data = await response.json();

        responseBox.innerHTML =
            data.response;

    }

    catch (error) {

        responseBox.innerHTML =
            "❌ Unable to connect to AI service.";

        console.error(error);
    }
}

// ==========================
// CTRL + ENTER SUPPORT
// ==========================

document.addEventListener(
    "DOMContentLoaded",
    () => {

        const questionBox =
            document.getElementById("question");

        if (questionBox) {

            questionBox.addEventListener(
                "keydown",
                function (event) {

                    if (
                        event.ctrlKey &&
                        event.key === "Enter"
                    ) {

                        askAI();
                    }
                }
            );
        }
    }
);

// ==========================
// DARK MODE TOGGLE
// ==========================

document.addEventListener(
    "DOMContentLoaded",
    () => {

        const toggle =
            document.getElementById("themeToggle");

        if (!toggle) return;

        const savedTheme =
            localStorage.getItem("theme");

        if (savedTheme === "dark") {

            document.body.classList.add("dark");

            toggle.innerHTML = "☀️";
        }

        toggle.addEventListener(
            "click",
            () => {

                document.body.classList.toggle("dark");

                if (
                    document.body.classList.contains("dark")
                ) {

                    localStorage.setItem(
                        "theme",
                        "dark"
                    );

                    toggle.innerHTML = "☀️";

                } else {

                    localStorage.setItem(
                        "theme",
                        "light"
                    );

                    toggle.innerHTML = "🌙";
                }
            }
        );
    }
);