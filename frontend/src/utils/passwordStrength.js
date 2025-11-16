export function calculateStrength(password) {
    const suggestions = [];
    let score = 0;

    if (password.length >= 12) score += 2;
    else if (password.length >= 8) score += 1;
    else suggestions.push("Increase password length to at least 12 characters.");

    if (/[A-Z]/.test(password)) score += 1;
    else suggestions.push("Add uppercase letters.");

    if (/[a-z]/.test(password)) score += 1;
    else suggestions.push("Add lowercase letters.");

    if (/\d/.test(password)) score += 1;
    else suggestions.push("Add numbers.");

    if (/[^A-Za-z0-9]/.test(password)) score += 1;
    else suggestions.push("Add symbols (e.g., !@#$%).");

    let level = "Weak";
    if (score >= 4) level = "Medium";
    if (score >= 6) level = "Strong";

    return { level, score, suggestions };
}

