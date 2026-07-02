// 独立媒体库管理

let selectedPhotoFiles = [];
let editingPhotoId = '';

function setDefaultPhotoDate() {
    const input = document.getElementById('photo-date');
    if (input.value) return;
    const now = new Date();
    const tzOffset = now.getTimezoneOffset() * 60000;
    input.value = new Date(now - tzOffset).toISOString().slice(0, 16);
}

function renderPhotoPreviews() {
    const container = document.getElementById('photo-previews');
    container.innerHTML = '';
    selectedPhotoFiles.forEach((file, index) => {
        const item = document.createElement('div');
        item.className = 'preview-item';

        const url = URL.createObjectURL(file);
        const preview = file.type.startsWith('video/')
            ? document.createElement('video')
            : document.createElement('img');
        preview.className = 'preview-img';
        preview.src = url;
        if (file.type.startsWith('video/')) {
            preview.muted = true;
            preview.playsInline = true;
        }
        if (file.type.startsWith('video/')) {
            preview.onloadedmetadata = () => URL.revokeObjectURL(url);
        } else {
            preview.onload = () => URL.revokeObjectURL(url);
        }

        const remove = document.createElement('span');
        remove.className = 'preview-remove';
        remove.textContent = '×';
        remove.onclick = () => {
            selectedPhotoFiles.splice(index, 1);
            renderPhotoPreviews();
        };

        item.appendChild(preview);
        item.appendChild(remove);
        container.appendChild(item);
    });
}

function addPhotoFiles(files) {
    if (!files.length) return;
    if (editingPhotoId && files.length > 1) {
        showToast('编辑时只能选择一张图片用于替换原图', true);
        selectedPhotoFiles = [files[0]];
    } else {
        selectedPhotoFiles = selectedPhotoFiles.concat(files);
    }
    renderPhotoPreviews();
}

function buildPhotoFormData() {
    if (!editingPhotoId && selectedPhotoFiles.length === 0) {
        showToast('请先选择要上传的图片或视频', true);
        return null;
    }
    const formData = new FormData();
    formData.append('title', document.getElementById('photo-title').value.trim());
    formData.append('date', document.getElementById('photo-date').value);
    formData.append('visibility', document.getElementById('photo-visibility').value);
    selectedPhotoFiles.forEach(file => formData.append('images', file));
    return formData;
}

async function loadPhotos() {
    const list = document.getElementById('photos-list');
    const count = document.getElementById('photos-count');
    try {
        const photos = await apiRequest('/api/photos');
        list.innerHTML = '';
        count.innerText = `${photos.length} 个`;

        if (photos.length === 0) {
            list.innerHTML = '<div class="empty-state"><span class="empty-icon">📸</span>还没有媒体，在左侧上传第一个吧</div>';
            return;
        }

        photos.forEach(photo => {
            const card = document.createElement('article');
            card.className = 'photo-admin-card';
            card.innerHTML = renderPhotoCard(photo);
            card.querySelector('[data-edit-photo]').onclick = () => editPhoto(photo);
            card.querySelector('[data-delete-photo]').onclick = () => deletePhoto(photo.id);
            list.appendChild(card);
        });
    } catch (e) {
        list.innerHTML = '<div class="empty-state">加载图片失败，请检查本地服务</div>';
    }
}

function renderPhotoCard(photo) {
    const privateBadge = photo.visibility === 'private' ? '<span class="memo-state private">私密</span>' : '<span class="memo-state">公开</span>';
    const media = photo.type === 'video'
        ? `<video src="${escapeHtml(photo.src)}" muted controls preload="metadata"></video>`
        : `<img src="${escapeHtml(photo.src)}" alt="">`;
    return `
        <a href="${escapeHtml(photo.src)}" target="_blank" rel="noopener noreferrer" class="photo-admin-cover">
            ${media}
        </a>
        <div class="photo-admin-body">
            <div class="photo-admin-title">${escapeHtml(photo.title || '未命名图片')}</div>
            <div class="photo-admin-meta">
                ${privateBadge}
                <span>${escapeHtml(formatMemoDate(photo.date))}</span>
                <span>${escapeHtml(photo.originalName || photo.filename || '')}</span>
            </div>
            <div class="actions">
                <button class="btn btn-secondary btn-icon" data-edit-photo>编辑</button>
                <button class="btn btn-danger btn-icon" data-delete-photo>删除</button>
            </div>
        </div>
    `;
}

function resetPhotoForm() {
    document.getElementById('photo-form').reset();
    document.getElementById('photo-edit-id').value = '';
    editingPhotoId = '';
    selectedPhotoFiles = [];
    renderPhotoPreviews();
    setDefaultPhotoDate();
    document.getElementById('photo-submit-btn').innerText = '上传媒体';
    document.getElementById('photo-upload-label').innerText = '上传图片 / 视频（可多选）';
    document.getElementById('photo-images-input').multiple = true;
}

function editPhoto(photo) {
    editingPhotoId = photo.id;
    selectedPhotoFiles = [];
    document.getElementById('photo-edit-id').value = photo.id;
    document.getElementById('photo-title').value = photo.title || '';
    document.getElementById('photo-date').value = toLocalInputValue(photo.date);
    document.getElementById('photo-visibility').value = photo.visibility || 'public';
    document.getElementById('photo-submit-btn').innerText = '保存图片';
    document.getElementById('photo-upload-label').innerText = '替换媒体文件（可不选）';
    document.getElementById('photo-images-input').multiple = false;
    renderPhotoPreviews();
    document.getElementById('photo-title').focus();
}

async function submitPhoto() {
    const formData = buildPhotoFormData();
    if (!formData) return;

    const btn = document.getElementById('photo-submit-btn');
    const isEditing = Boolean(editingPhotoId);
    btn.disabled = true;
    btn.innerText = isEditing ? '正在保存...' : '正在上传...';

    try {
        const url = isEditing ? `/api/photos/${encodeURIComponent(editingPhotoId)}` : '/api/photos';
        const method = isEditing ? 'PUT' : 'POST';
        const data = await apiRequest(url, { method, body: formData });
        if (data.status === 'success') {
            showToast(isEditing ? '媒体已更新！' : `已上传 ${data.count || 1} 个媒体！`);
            resetPhotoForm();
            loadPhotos();
        } else {
            showToast(data.message, true);
        }
    } catch (e) {
        showToast('网络错误，保存失败', true);
    } finally {
        btn.disabled = false;
        btn.innerText = editingPhotoId ? '保存图片' : '上传图片';
    }
}

async function deletePhoto(id) {
    if (!confirm('确定要删除这个媒体吗？原文件也会一同清理。')) return;
    try {
        const data = await apiRequest(`/api/photos/${encodeURIComponent(id)}`, { method: 'DELETE' });
        if (data.status === 'success') {
            showToast('媒体已删除！');
            if (editingPhotoId === id) resetPhotoForm();
            loadPhotos();
        } else {
            showToast(data.message, true);
        }
    } catch (e) {
        showToast('网络错误，删除失败', true);
    }
}

function initPhotos() {
    const input = document.getElementById('photo-images-input');
    const dropzone = document.getElementById('photo-dropzone');

    setDefaultPhotoDate();
    dropzone.addEventListener('click', () => input.click());

    input.addEventListener('change', (e) => {
        addPhotoFiles(Array.from(e.target.files).filter(isSupportedMediaFile));
        e.target.value = '';
    });

    dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.classList.add('dragover');
    });
    dropzone.addEventListener('dragleave', () => dropzone.classList.remove('dragover'));
    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
        addPhotoFiles(Array.from(e.dataTransfer.files).filter(isSupportedMediaFile));
    });

    document.getElementById('photo-submit-btn').addEventListener('click', submitPhoto);
    document.getElementById('photo-reset-btn').addEventListener('click', resetPhotoForm);
}

function isSupportedMediaFile(file) {
    return file.type.startsWith('image/') || file.type.startsWith('video/');
}
