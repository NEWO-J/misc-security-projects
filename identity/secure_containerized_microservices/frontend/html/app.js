const form = document.getElementById('auth');
const regform = document.getElementById('register');
const greeting = document.getElementById('greeting');
const errorMsg = document.getElementById('errormsg')

if (form) {
    form.addEventListener('submit', (event) => {
        event.preventDefault();

        const formData = new FormData(form);
        const formObject = Object.fromEntries(formData);

        authenticate('https://localhost:8082/auth', formObject);

    })
}

if (regform) {
regform.addEventListener('submit', (event) => {
    event.preventDefault();

    const regData = new FormData(regform);
    const regObject = Object.fromEntries(regData);

    register('https://localhost:8082/register', regObject);
})

}

async function authenticate(url, payload) {
    try {
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
                
            },
            credentials: `include`,
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (!response.ok) {
            const errorMessage = data.detail || `HTTP Error! Status ${response.status}`;
            throw new Error(errorMessage);
        };
    
        window.location.href = `https://localhost:8082/dashboard`;

    } catch (error) {
        errorMsg.textContent = error.message;
        console.error("Error sending POST request:", error.message);
    }
}

async function register(url, payload) {
    try {
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (!response.ok) {
            const errorMessage = data.detail || `HTTP Error! Status ${response.status}`;
            throw new Error(errorMessage);
        }

        window.location.href = data["redirect_url"];

        
    } catch (error) {
        errorMsg.textContent = error.message;
        console.log("Error sending post request: ", error.message);
    }

}