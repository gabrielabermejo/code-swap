function convertCode() {
    const inputCode = document.getElementById('input-code').value;
    const direction = document.getElementById('conversion-direction').value;

    fetch('/convert', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ code: inputCode, direction: direction })
    })
    .then(response => response.json())
    .then(data => {
        if (data.converted_code) {
            document.getElementById('output-code').value = data.converted_code;
        } else if (data.error) {
            document.getElementById('output-code').value = 'Error: ' + data.error;
        } else {
            document.getElementById('output-code').value = 'Unexpected response';
        }
    })
    .catch(error => {
        document.getElementById('output-code').value = 'Request failed: ' + error;
    });
}
