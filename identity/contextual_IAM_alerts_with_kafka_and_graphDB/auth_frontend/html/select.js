const mail = document.getElementById("mail");
const ftp = document.getElementById("ftp");
const db = document.getElementById("db");
const test = document.getElementById("test");

mail.addEventListener("click", function() {
    window.location.href = "https://localhost:8080/auth?service=mail";
});

ftp.addEventListener("click", function() {
    window.location.href = "https://localhost:8080/auth?service=ftp";
});

db.addEventListener("click", function() {
    window.location.href = "https://localhost:8080/auth?service=db";
});

test.addEventListener("click", function() {
    window.location.href = "https://localhost:8080/auth?service=test";
});
