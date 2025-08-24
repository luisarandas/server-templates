// Upload listener
document.getElementById('uploadform').addEventListener('submit', async function(e) {
    e.preventDefault();
    const formData = new FormData(this);
    for (const file of document.querySelector('input[type="file"]').files) {
        console.log(file.name, file.type); // Check files being uploaded
        formData.append('files', file); // match 'files' with the FastAPI function parameter
    }
    const response = await fetch('/uploadimages', {
        method: 'POST',
        body: formData,
    });
    if (response.ok) {
        const data = await response.json();
        console.log(data);
        const placeholder = document.querySelector('.imageplaceholder1');
        placeholder.innerHTML = ''; // Clear
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


// Classifier listener
document.getElementById('process_1').addEventListener('click', async () => {
    const placeholder = document.querySelector('.imageplaceholder1');
    const imgElement = placeholder.querySelector('img:last-child');
    if (imgElement) {
        const imageUrl = imgElement.src;
        const response = await fetch(imageUrl);
        const imageBlob = await response.blob();
        const formData = new FormData();
        formData.append('image', imageBlob, 'image.png');
        console.log("New form data: ", formData);
        const processResponse = await fetch('/process-last-image', {
            method: 'POST',
            body: formData, 
        });
        if (processResponse.ok) {
            const data = await processResponse.json();
            console.log("This is the processed response data: ", data);
            const placeholder2 = document.querySelector('.imageplaceholder2');
            placeholder2.innerHTML = ''; // Clear
            const textNode = document.createElement('p'); // Creating a paragraph element to hold the results
            textNode.textContent = `${data.classification}`; // Add the results as text content
            placeholder2.appendChild(textNode);
            placeholder2.style.color = 'black';
        } else {
            console.error('Failed to process the image');
        }
    } else {
        console.error('No image to process');
    }
});

