 document.addEventListener("alpine:init", () => {
        Alpine.data("dropdown", () => ({
            open: false,
            toggle() {
                    this.open = !this.open
            },
            show: 'see reviews',
            close: 'close reviews',
            openModal: false,
            toggleModal() {
                this.openModal = !this.openModal
            },
            openReviewForm: false,
            toggleReviewForm() {
                this.openReviewForm = !this.openReviewForm
            },
            toggleMenu() {
                const menu = document.querySelector(".menu").classList.toggle("expand");

            }
        })
        )
    })