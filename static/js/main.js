function incrementQuantity(button) {
    const input = button.parentElement.querySelector('input[name="quantity"]');
    let value = parseInt(input.value);
    if (value < 10) {
        input.value = value + 1;
        input.form.submit();
    }
}

function decrementQuantity(button) {
    const input = button.parentElement.querySelector('input[name="quantity"]');
    let value = parseInt(input.value);
    if (value > 0) {
        input.value = value - 1;
        input.form.submit();
    }
}

// Smooth scroll for anchor links (optional)
document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener("click", function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute("href")).scrollIntoView({
                behavior: "smooth"
            });
        });
    });
});




