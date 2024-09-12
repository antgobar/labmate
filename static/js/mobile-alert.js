document.addEventListener('DOMContentLoaded', () => {
    const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
    const modal = document.getElementById('mobile-alert');

    if (isMobile) {
        // Check if the user has already seen the modal
        if (!localStorage.getItem('modalSeen')) {
            modal.showModal();
        }
    }

    // Close the modal and set local storage
    document.querySelectorAll('[data-close]').forEach(button => {
        button.addEventListener('click', () => {
            modal.close();
            localStorage.setItem('modalSeen', 'true');
        });
    });
});