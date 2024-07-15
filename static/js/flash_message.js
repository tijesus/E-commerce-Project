const handle_flash_message = () => {
    const flash_message = document.querySelector(".alert");
    const close_message = document.querySelector(".close__message");

    if (flash_message) {
        close_message.addEventListener("click", (e) => {
            flash_message.remove()
            e.target.remove()
        })
        setInterval(() => {
            flash_message.remove()
            close_message.remove()
        }, 4000)

    }
}


// Run setupFlashMessages on initial page load
    document.addEventListener("DOMContentLoaded", handle_flash_message);

    // Run setupFlashMessages after HTMX swaps content
    document.body.addEventListener('htmx:afterSwap', (event) => {
        if (event && event.target.id === "flash-messages") {
            handle_flash_message();
        }
    });
