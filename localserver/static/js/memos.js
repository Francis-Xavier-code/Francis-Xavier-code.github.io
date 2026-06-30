// 瞬间记录

let selectedFiles = [];

async function loadMemos() {
    const list = document.getElementById('memos-list');
    try {
        const memos = await apiRequest('/api/memos');
        list.innerHTML = '';

        if (memos.length === 0) {
            list.innerHTML = '<div class="empty-state"><span class="empty-icon">🫧</span>还没有记录任何瞬间，在上方写下第一条吧</div>';
            return;
        }

        memos.forEach(memo => {
            let imgHtml = '';
            if (memo.images && memo.images.length > 0) {
                imgHtml = '<div style="display: flex; gap: 8px; margin-top: 10px; flex-wrap: wrap;">';
                memo.images.forEach(img => {
                    imgHtml += `<img src="${escapeHtml(img)}" class="memo-thumb">`;
                });
                imgHtml += '</div>';
            }

            const dateStr = memo.date ? memo.date.replace('T', ' ').substring(0, 16) : '无时间';
            const safeContent = escapeHtml(memo.content);
            const safeId = escapeHtml(memo.id);

            const row = document.createElement('div');
            row.className = 'list-row';
            row.style.alignItems = 'flex-start';
            row.innerHTML = `
                <div class="item-meta" style="flex-grow: 1;">
                    <div style="font-size: 14px; white-space: pre-wrap; color: var(--text-color); line-height: 1.6; word-break: break-word;">${safeContent}</div>
                    ${imgHtml}
                    <div style="font-size: 11px; color: var(--text-muted); margin-top: 10px;">
                        <span>📅 ${dateStr}</span> &middot; <span>文件: ${safeId}</span>
                    </div>
                </div>
                <div class="actions" style="align-self: center;">
                    <button class="btn btn-danger btn-icon" data-delete>🗑️ 删除</button>
                </div>
            `;
            row.querySelector('[data-delete]').onclick = () => deleteMemo(memo.id);
            list.appendChild(row);
        });
    } catch (e) {
        list.innerHTML = '<div class="empty-state">加载瞬间失败，请检查本地服务</div>';
    }
}

function addFiles(files) {
    if (files.length === 0) return;
    if (selectedFiles.length + files.length > 9) {
        showToast('瞬间最多只能上传 9 张照片！', true);
        return;
    }
    selectedFiles = selectedFiles.concat(files);
    renderPreviews();
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
        remove.textContent = '✕';
        remove.onclick = () => {
            selectedFiles.splice(index, 1);
            renderPreviews();
        };

        item.appendChild(img);
        item.appendChild(remove);
        container.appendChild(item);
    });
}

async function submitMemo() {
    const content = document.getElementById('memo-content').value.trim();
    if (!content) {
        showToast('内容不能为空！', true);
        return;
    }

    const btn = document.getElementById('memo-submit-btn');
    btn.disabled = true;
    btn.innerText = '正在发布...';

    const formData = new FormData();
    formData.append('content', content);
    selectedFiles.forEach(file => formData.append('images', file));

    try {
        const data = await apiRequest('/api/memos', { method: 'POST', body: formData });
        if (data.status === 'success') {
            showToast('瞬间发布成功！');
            document.getElementById('memo-content').value = '';
            selectedFiles = [];
            renderPreviews();
            loadMemos();
        } else {
            showToast(data.message, true);
        }
    } catch (err) {
        showToast('网络错误，发布失败', true);
    } finally {
        btn.disabled = false;
        btn.innerText = '发布瞬间';
    }
}

async function deleteMemo(id) {
    if (!confirm('确定要删除这条瞬间吗？图片文件也会一同清理。')) return;
    try {
        const data = await apiRequest(`/api/memos/${encodeURIComponent(id)}`, { method: 'DELETE' });
        if (data.status === 'success') {
            showToast('删除瞬间成功！');
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
}
