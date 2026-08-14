const title = document.getElementById("title");
const header = document.getElementById("header");
const perms = document.getElementById("perms");

const params = new URLSearchParams(window.location.search);
const service = params.get('service');

getservice(service);

async function getservice(service) {
    try {
        const response = await fetch(`https://localhost:8080/api/verify?service=${service}`);

        if (!response.ok) {
            errorMsg.textContent = error.message;
            console.error("Error sending POST request:", error.message);
            window.location.href = "/auth";
            return;
        }

        const data = await response.json();
        title.innerText = `${service} dashboard`;
        header.innerText = `Welcome to the ${service} service`;
        perms.innerText = `Permissions: ${data["perms"][service].join(', ')}`;



    } catch (error) {
        console.error("Error sending POST request:", error.message);
        window.location.href = "/auth";
    }
}