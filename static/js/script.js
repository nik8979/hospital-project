document.getElementById('fileForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const file = document.getElementById('fileInput').files[0];
    
    if (file) {
        const formData = new FormData();
        formData.append("file", file);

        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();
        document.getElementById('message').innerText = result.message;
        document.getElementById('message').style.color = response.ok ? 'green' : 'red'; // Set message color based on response
    }
});
