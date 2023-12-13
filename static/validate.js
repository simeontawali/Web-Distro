// add a listener so that when the document loads . . .
window.addEventListener("DOMContentLoaded", async () => {
    // get reference to the form fields
    const emailField = document.getElementById("email-input");
    const pwdField = document.getElementById("pwd-input");
    const pwdMatch = document.getElementById("pwd-confirm");

    // add handlers to validate different fields for validation
    emailField.addEventListener("change", validateEmail);
    pwdMatch.addEventListener("change", checkMatchingPasswords);
    pwdField.addEventListener("change", checkMatchingPasswords);
    pwdField.addEventListener("change", restrictBreachedPasswords);
});

function validateEmail() {
    const emailRegex = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    //get the current text in the email field
    const emailField = document.getElementById("email-input");
    const email = emailField.value;
    const msg = emailRegex.test(email) ? "" : "A valid email address is required!";
    emailField.setCustomValidity(msg);
}

function checkMatchingPasswords() {
    const pwdField = document.getElementById("pwd-input");
    const pwdMatch = document.getElementById("pwd-confirm");
    const msg = (pwdField.value === pwdMatch.value) ? "" : "Password do not match!";
    pwdMatch.setCustomValidity(msg);
}

async function restrictBreachedPasswords() {
    const pwdField = document.getElementById("pwd-input");
    const breachCount = await knownPasswordBreaches();
    const msg = (breachCount < 10) ? "" : `Password appears ${breachCount} times in known breaches`;
    pwdField.setCustomValidity(msg);
}

async function knownPasswordBreaches() {
    
    const pwdField = document.getElementById("pwd-input");
    const pwdHash = sha1(pwdField.value).toUpperCase();
   
    const hashPrefix = pwdHash.slice(0,5);
    const apiURL = `https://api.pwnedpasswords.com/range/${hashPrefix}`;
    
    const r = await fetch(apiURL);
    
    const text = await r.text();
   
    for (const line of text.split("\n")){
        const parts = line.split(";");
        const possibleHash = (hashPrefix + parts[0].trim()).toUpperCase();

        if (possibleHash === pwdHash){
            const count = parseInt(parts[1]);
            return count;
        }
    }

    return 0;
}
