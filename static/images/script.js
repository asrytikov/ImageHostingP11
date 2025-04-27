const tbody = document.getElementById('imagesTableBody');
let currentPage = 1;
const imagesPerPage = 10;

function setImages(images) {
    images.forEach(image => {
        const tr = document.createElement('tr');
        const tdPreview = document.createElement('td');
        const tdUrl = document.createElement('td');
        const tdSize = document.createElement('td');
        const tdTime = document.createElement('td');
        const tdDelete = document.createElement('td');
        const deleteButton = document.createElement('button');
        const fullFilename = encodeURIComponent(image.filename + image.file_type);
        deleteButton.onclick = () => {
            fetch(`/api/delete/${fullFilename}`, { method: 'DELETE' })
                .then(() => loadImages(currentPage))
                .catch(error => console.error(error));
        }
        deleteButton.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-x-lg" viewBox="0 0 16 16"> <path d="M2.146 2.854a.5.5 0 1 1 .708-.708L8 7.293l5.146-5.147a.5.5 0 0 1 .708.708L8.707 8l5.147 5.146a.5.5 0 0 1-.708.708L8 8.707l-5.146 5.147a.5.5 0 0 1-.708-.708L7.293 8z"/></svg>';
        deleteButton.classList.add('delete-btn');
        tdDelete.appendChild(deleteButton);

        tdPreview.innerHTML = `<img src="/images/${fullFilename}" width="42" height="100%">`;
        tdUrl.innerHTML = `<a href="/images/${fullFilename}" target="_blank">${image.original_name}${image.file_type}</a>`;
        tdSize.innerHTML = image.size;
        tdTime.innerHTML = image.upload_date;

        tr.appendChild(tdPreview);
        tr.appendChild(tdUrl);
        tr.appendChild(tdSize);
        tr.appendChild(tdTime);
        tr.appendChild(tdDelete);

        tbody.appendChild(tr);
    });
}

function loadImages(page) {
    fetch(`/api/images/?page=${page}`)
        .then(response => response.json())
        .then(data => {
        if (data.images.length == 0) {
            document.querySelector('main').style.display = 'none';
            document.body.appendChild(document.createElement('h1')).textContent = 'Нет загруженных изображений';

        } else {
            tbody.innerHTML = '';
            setImages(data.images);
            document.getElementById('nextPage').disabled = data.images.length < imagesPerPage;
            document.getElementById('prevPage').disabled = page === 1;
            document.getElementById('currentPage').textContent = page;
            currentPage = page;
        }
    })
    .catch(error => console.error(error));
}

document.getElementById('btnGoToUpload').addEventListener('click', (event) => {
    window.location.href = '/upload/';
});

document.getElementById('prevPage').addEventListener('click', () => {
    if (currentPage > 1) {
        loadImages(currentPage - 1);
    }
});

document.getElementById('nextPage').addEventListener('click', () => {
    loadImages(currentPage + 1);
});

loadImages(1);
