// efecto
const canvas = document.createElement('canvas');
document.body.appendChild(canvas);
const context = canvas.getContext('2d');

canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

const letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890';
const fontSize = 16;
const columns = canvas.width / fontSize;

const drops = [];
for (let x = 0; x < columns; x++) {
    drops[x] = 1;
}

function draw() {
    context.fillStyle = 'rgba(0, 0, 0, 0.05)';
    context.fillRect(0, 0, canvas.width, canvas.height);

    context.fillStyle = '#BB86FC';
    context.font = fontSize + 'px monospace';

    for (let i = 0; i < drops.length; i++) {
        const text = letters.charAt(Math.floor(Math.random() * letters.length));
        context.fillText(text, i * fontSize, drops[i] * fontSize);

        if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
            drops[i] = 0;
        }

        drops[i]++;
    }
}

setInterval(draw, 33);

window.addEventListener('resize', () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
});

// Convert code functionality
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

// Copy to clipboard functionality
function copyToClipboard() {
    const outputCode = document.getElementById('output-code');
    outputCode.select();
    document.execCommand('copy');
    alert('Código copiado al portapapeles!');
}
