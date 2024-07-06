function sendRequest(url) {
            fetch(url)
            .then(response => {
                if (response.ok) {
                    return response.json(); // Assuming you expect JSON data
                }
                throw new Error('Network response was not ok.');
            })
            .then(data => {
                // Handle the success response (status 200)
                createSuccessButton();
                removeGenerateTokenElement();
            })
            .catch(error => {
                console.error('There has been a problem with your fetch operation:', error);
            });
        }

        function createSuccessButton() {
            const button = document.createElement('button');
            button.textContent = 'Success';
            button.classList.add('form__button');
            button.style.backgroundColor = 'green';

            button.disabled = true;

            // button.style.paddingInline = '1rem'
            // button.style.paddingBlock = '.5rem'

            const generateTokenElement = document.querySelector('.generate_token');
            if (generateTokenElement) {
                generateTokenElement.insertAdjacentElement('afterend', button);
            }
        }

        function removeGenerateTokenElement() {
            const generateTokenElement = document.querySelector('.generate_token');
            if (generateTokenElement) {
                generateTokenElement.remove();
            }
        }