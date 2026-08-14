const form = document.getElementById("auth")

const params = new URLSearchParams(window.location.search);
const service = params.get('service');
if (!service) {
    window.location.href = "/";
}

form.addEventListener('submit', (event) => {
    event.preventDefault();

    const formData = new FormData(form);
    const formObject = Object.fromEntries(formData);

    const params = new URLSearchParams(window.location.search);
    const service = params.get('service');

    authenticate(formObject, service);
})

async function authenticate(payload, service) {
    try {
        const response = await fetch("https://localhost:8080/login", { 
            method: "POST", 
            headers: {
                "Content-Type": "application/json",
                "Service": service
            },
            credentials: 'include',
            body: JSON.stringify(payload)
            
        });

        const data = await response.json();
        
        if (!response.ok) {
            console.error("Error")
        } else {
            window.location.href = `https://localhost:8080/service?service=${service}`;
        }

    } catch (error) {
        console.error("Error sending request", error);
    }


}
    