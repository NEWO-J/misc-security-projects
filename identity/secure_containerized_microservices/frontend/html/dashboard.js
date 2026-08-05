const urlParams = new URLSearchParams(window.location.search);
const greeting = document.getElementById("greeting");
const errorMsg = document.getElementById("errormsg");

async function verify_token() {

    try {
        const response = await fetch(`https://localhost:8082/api/verify`)
        const data = await response.json();

        if (!response.ok) {
            errorMsg.textContent = error.message;
            console.error("Error sending POST request:", error.message);
            window.location.href = "/login";
        }

            greeting.innerText = `Hello ${data["user"]}`;


    } catch (error) {
        errorMsg.textContent = error.message;
        console.error("Error sending POST request:", error.message);
        window.location.href = "/login";
    }
}

if (greeting) {
    verify_token();
}
