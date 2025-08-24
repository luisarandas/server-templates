// Upload listener
document.getElementById('uploadform').addEventListener('submit', async function(e) {
    e.preventDefault();
    const formData = new FormData(this);
    for (const file of document.querySelector('input[type="file"]').files) {
        console.log(file.name, file.type);
        formData.append('files', file);
    }
    const response = await fetch('/uploadimages', {
        method: 'POST',
        body: formData,
    });
    if (response.ok) {
        const data = await response.json();
        console.log(data);
        const placeholder = document.querySelector('.imageplaceholder1');
        placeholder.innerHTML = '';
        placeholder.style.backgroundColor = 'black';
        if (data.image_urls && data.image_urls.length > 0) {
            data.image_urls.forEach(url => {
                const img = document.createElement('img');
                img.style.height = '100%';
                img.style.maxWidth = '100%';
                img.src = url;
                img.id = 'uploadedImage';
                placeholder.appendChild(img);
            });
        } else {
            console.error('No images returned', data);
        }
    } else {
        console.error('Upload failed');
    }
});

// Server status checker
async function checkServerStatus() {
    try {
        const response = await fetch('/health');
        if (response.ok) {
            const data = await response.json();
            const placeholder2 = document.querySelector('.imageplaceholder2');
            placeholder2.innerHTML = '';
            const statusNode = document.createElement('p');
            statusNode.textContent = `Server Status: ${data.status}`;
            statusNode.style.color = '#ffffff';
            placeholder2.appendChild(statusNode);
        }
    } catch (error) {
        console.error('Failed to check server status:', error);
    }
}

// Check server status on page load
document.addEventListener('DOMContentLoaded', function() {
    checkServerStatus();
});

