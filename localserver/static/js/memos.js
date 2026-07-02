// 瞬间记录

let selectedFiles = [];
let existingImages = [];
let editingMemoId = '';

function toLocalInputValue(dateValue) {
    if (!dateValue) return '';
    return dateValue.replace('+08:00', '').substring(0, 16);
}

function formatMemoDate(dateValue) {
    if (!dateValue) return '无时间';
    return dateValue.replace('T', ' ').replace('+08:00', '').substring(0, 16);
}

function setDefaultMemoDate() {
    const input = document.getElementById('memo-date');
    if (input.value) return;
    const now = new Date();
    const tzOffset = now.getTimezoneOffset() * 60000;
    input.value = new Date(now - tzOffset).toISOString().slice(0, 16);
}

async function loadMemos() {
    const list = document.getElementById('memos-list');
    const count = document.getElementById('memo-count');
    try {
        const memos = await apiRequest('/api/memos');
        list.innerHTML = '';
        count.innerText = `${memos.length} 条`;

        if (memos.length === 0) {
            list.innerHTML = '<div class="empty-state"><span class="empty-icon">🫧</span>还没有记录任何瞬间，在左侧写下第一条吧</div>';
            return;
        }

        memos.forEach(memo => {
            const row = document.createElement('article');
            row.className = 'memo-admin-card';
            row.innerHTML = renderMemoCard(memo);
            row.querySelector('[data-edit]').onclick = () => editMemo(memo);
            row.querySelector('[data-delete]').onclick = () => deleteMemo(memo.id);
            list.appendChild(row);
        });
    } catch (e) {
        list.innerHTML = '<div class="empty-state">加载瞬间失败，请检查本地服务</div>';
    }
}

function renderMemoCard(memo) {
    const images = Array.isArray(memo.images) ? memo.images : [];
    const tags = Array.isArray(memo.tags) ? memo.tags : [];
    const imageHtml = images.length ? `
        <div class="memo-admin-gallery gallery-${Math.min(images.length, 4)}">
            ${images.map(img => `<img src="${escapeHtml(img)}" alt="">`).join('')}
        </div>
    ` : '';
    const tagHtml = tags.length ? `
        <div class="memo-admin-tags">
            ${tags.map(tag => `<span>#${escapeHtml(tag)}</span>`).join('')}
        </div>
    ` : '';
    const visibility = memo.visibility === 'private'
        ? '<span class="memo-state private">私密</span>'
        : '<span class="memo-state">公开</span>';

    return `
        <div class="memo-admin-main">
            <div class="memo-admin-date">${escapeHtml(formatMemoDate(memo.date))}</div>
            <div class="memo-admin-content">${escapeHtml(memo.content)}</div>
            ${imageHtml}
            <div class="memo-admin-meta">
                ${visibility}
                ${memo.location ? `<span>地点：${escapeHtml(memo.location)}</span>` : ''}
                ${memo.mood ? `<span>心情：${escapeHtml(memo.mood)}</span>` : ''}
                <span>文件：${escapeHtml(memo.id)}</span>
            </div>
            ${tagHtml}
        </div>
        <div class="actions memo-card-actions">
            <button class="btn btn-secondary btn-icon" data-edit>编辑</button>
            <button class="btn btn-danger btn-icon" data-delete>删除</button>
        </div>
    `;
}

function addFiles(files) {
    if (files.length === 0) return;
    if (selectedFiles.length + existingImages.length + files.length > 9) {
        showToast('瞬间最多只能上传 9 张照片！', true);
        return;
    }
    selectedFiles = selectedFiles.concat(files);
    renderPreviews();
}

function renderExistingImages() {
    const container = document.getElementById('existing-images');
    container.innerHTML = '';
    existingImages.forEach((src, index) => {
        const item = document.createElement('div');
        item.className = 'preview-item';
        item.innerHTML = `
            <img class="preview-img" src="${escapeHtml(src)}" alt="">
            <span class="preview-remove" title="移除图片">×</span>
        `;
        item.querySelector('.preview-remove').onclick = () => {
            existingImages.splice(index, 1);
            renderExistingImages();
        };
        container.appendChild(item);
    });
}

function renderPreviews() {
    const container = document.getElementById('previews');
    container.innerHTML = '';
    selectedFiles.forEach((file, index) => {
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
            selectedFiles.splice(index, 1);
            renderPreviews();
        };

        item.appendChild(img);
        item.appendChild(remove);
        container.appendChild(item);
    });
}

function resetMemoForm() {
    document.getElementById('memo-form').reset();
    document.getElementById('memo-edit-id').value = '';
    editingMemoId = '';
    selectedFiles = [];
    existingImages = [];
    renderExistingImages();
    renderPreviews();
    setDefaultMemoDate();
    document.getElementById('memo-submit-btn').innerText = '发布瞬间';
}

function editMemo(memo) {
    editingMemoId = memo.id;
    existingImages = Array.isArray(memo.images) ? memo.images.slice() : [];
    selectedFiles = [];

    document.getElementById('memo-edit-id').value = memo.id;
    document.getElementById('memo-content').value = memo.content || '';
    document.getElementById('memo-date').value = toLocalInputValue(memo.date);
    document.getElementById('memo-location').value = memo.location || '';
    document.getElementById('memo-mood').value = memo.mood || '';
    document.getElementById('memo-tags').value = Array.isArray(memo.tags) ? memo.tags.join(' ') : '';
    document.getElementById('memo-visibility').value = memo.visibility || 'public';
    document.getElementById('memo-submit-btn').innerText = '保存修改';
    renderExistingImages();
    renderPreviews();
    document.getElementById('memo-content').focus();
}

function buildMemoFormData() {
    const content = document.getElementById('memo-content').value.trim();
    if (!content) {
        showToast('内容不能为空！', true);
        return null;
    }

    const formData = new FormData();
    formData.append('content', content);
    formData.append('date', document.getElementById('memo-date').value);
    formData.append('location', document.getElementById('memo-location').value.trim());
    formData.append('mood', document.getElementById('memo-mood').value.trim());
    formData.append('tags', document.getElementById('memo-tags').value.trim());
    formData.append('visibility', document.getElementById('memo-visibility').value);
    formData.append('existing_images', JSON.stringify(existingImages));
    selectedFiles.forEach(file => formData.append('images', file));
    return formData;
}

async function submitMemo() {
    const formData = buildMemoFormData();
    if (!formData) return;

    const btn = document.getElementById('memo-submit-btn');
    const isEditing = Boolean(editingMemoId);
    btn.disabled = true;
    btn.innerText = isEditing ? '正在保存...' : '正在发布...';

    try {
        const url = isEditing ? `/api/memos/${encodeURIComponent(editingMemoId)}` : '/api/memos';
        const method = isEditing ? 'PUT' : 'POST';
        const data = await apiRequest(url, { method, body: formData });
        if (data.status === 'success') {
            showToast(isEditing ? '瞬间已更新！' : '瞬间发布成功！');
            resetMemoForm();
            loadMemos();
        } else {
            showToast(data.message, true);
        }
    } catch (err) {
        showToast('网络错误，保存失败', true);
    } finally {
        btn.disabled = false;
        btn.innerText = editingMemoId ? '保存修改' : '发布瞬间';
    }
}

async function deleteMemo(id) {
    if (!confirm('确定要删除这条瞬间吗？图片文件也会一同清理。')) return;
    try {
        const data = await apiRequest(`/api/memos/${encodeURIComponent(id)}`, { method: 'DELETE' });
        if (data.status === 'success') {
            showToast('删除瞬间成功！');
            if (editingMemoId === id) resetMemoForm();
            loadMemos();
        } else {
            showToast(data.message, true);
        }
    } catch (e) {
        showToast('网络错误，删除失败', true);
    }
}

// 绑定瞬间页面的交互（拖拽 / 选择 / 发布）
function initMemos() {
    const input = document.getElementById('memo-images-input');
    const dropzone = document.getElementById('dropzone');

    setDefaultMemoDate();
    dropzone.addEventListener('click', () => input.click());

    input.addEventListener('change', (e) => {
        addFiles(Array.from(e.target.files));
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
        const files = Array.from(e.dataTransfer.files).filter(f => f.type.startsWith('image/'));
        addFiles(files);
    });

    document.getElementById('memo-submit-btn').addEventListener('click', submitMemo);
    document.getElementById('memo-reset-btn').addEventListener('click', resetMemoForm);
}
