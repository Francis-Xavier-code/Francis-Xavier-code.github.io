// 独立图片库管理

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

        const img = document.createElement('img');
        img.className = 'preview-img';
        img.src = URL.createObjectURL(file);
        img.onload = () => URL.revokeObjectURL(img.src);

        const remove = document.createElement('span');
        remove.className = 'preview-remove';
        remove.textContent = '×';
        remove.onclick = () => {
            selectedPhotoFiles.splice(index, 1);
            renderPhotoPreviews();
        };

        item.appendChild(img);
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
        showToast('请先选择要上传的图片', true);
        return null;
    }
    const formData = new FormData();
    formData.append('title', document.getElementById('photo-title').value.trim());
    formData.append('date', document.getElementById('photo-date').value);
    formData.append('location', document.getElementById('photo-location').value.trim());
    formData.append('visibility', document.getElementById('photo-visibility').value);
    formData.append('tags', document.getElementById('photo-tags').value.trim());
    formData.append('description', document.getElementById('photo-description').value.trim());
    selectedPhotoFiles.forEach(file => formData.append('images', file));
    return formData;
}

async function loadPhotos() {
    const list = document.getElementById('photos-list');
    const count = document.getElementById('photos-count');
    try {
        const photos = await apiRequest('/api/photos');
        list.innerHTML = '';
        count.innerText = `${photos.length} 张`;

        if (photos.length === 0) {
            list.innerHTML = '<div class="empty-state"><span class="empty-icon">📸</span>还没有独立图片，在左侧上传第一张吧</div>';
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
    const tags = Array.isArray(photo.tags) ? photo.tags : [];
    const privateBadge = photo.visibility === 'private' ? '<span class="memo-state private">私密</span>' : '<span class="memo-state">公开</span>';
    return `
        <a href="${escapeHtml(photo.src)}" target="_blank" rel="noopener noreferrer" class="photo-admin-cover">
            <img src="${escapeHtml(photo.src)}" alt="">
        </a>
        <div class="photo-admin-body">
            <div class="photo-admin-title">${escapeHtml(photo.title || '未命名图片')}</div>
            <div class="photo-admin-meta">
                ${privateBadge}
                <span>${escapeHtml(formatMemoDate(photo.date))}</span>
                ${photo.location ? `<span>${escapeHtml(photo.location)}</span>` : ''}
            </div>
            ${photo.description ? `<div class="photo-admin-desc">${escapeHtml(photo.description)}</div>` : ''}
            ${tags.length ? `<div class="photo-admin-tags">${tags.map(tag => `<span>#${escapeHtml(tag)}</span>`).join('')}</div>` : ''}
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
    document.getElementById('photo-submit-btn').innerText = '上传图片';
    document.getElementById('photo-upload-label').innerText = '上传原图（可多选）';
    document.getElementById('photo-images-input').multiple = true;
}

function editPhoto(photo) {
    editingPhotoId = photo.id;
    selectedPhotoFiles = [];
    document.getElementById('photo-edit-id').value = photo.id;
    document.getElementById('photo-title').value = photo.title || '';
    document.getElementById('photo-date').value = toLocalInputValue(photo.date);
    document.getElementById('photo-location').value = photo.location || '';
    document.getElementById('photo-visibility').value = photo.visibility || 'public';
    document.getElementById('photo-tags').value = Array.isArray(photo.tags) ? photo.tags.join(' ') : '';
    document.getElementById('photo-description').value = photo.description || '';
    document.getElementById('photo-submit-btn').innerText = '保存图片';
    document.getElementById('photo-upload-label').innerText = '替换原图（可不选）';
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
            showToast(isEditing ? '图片已更新！' : `已上传 ${data.count || 1} 张图片！`);
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
    if (!confirm('确定要删除这张图片吗？原图文件也会一同清理。')) return;
    try {
        const data = await apiRequest(`/api/photos/${encodeURIComponent(id)}`, { method: 'DELETE' });
        if (data.status === 'success') {
            showToast('图片已删除！');
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
        addPhotoFiles(Array.from(e.target.files).filter(f => f.type.startsWith('image/')));
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
        addPhotoFiles(Array.from(e.dataTransfer.files).filter(f => f.type.startsWith('image/')));
    });

    document.getElementById('photo-submit-btn').addEventListener('click', submitPhoto);
    document.getElementById('photo-reset-btn').addEventListener('click', resetPhotoForm);
}
