// 图库预览

function flattenMemoImages(memos) {
    const photos = [];
    memos.forEach(memo => {
        const images = Array.isArray(memo.images) ? memo.images : [];
        images.forEach((src, index) => {
            photos.push({
                src,
                index,
                memo,
            });
        });
    });
    return photos;
}

async function loadGallery() {
    const list = document.getElementById('gallery-list');
    const count = document.getElementById('gallery-count');
    try {
        const memos = await apiRequest('/api/memos');
        const photos = flattenMemoImages(memos);
        list.innerHTML = '';
        count.innerText = `${photos.length} 张`;

        if (photos.length === 0) {
            list.innerHTML = '<div class="empty-state"><span class="empty-icon">🖼️</span>还没有图片。去瞬间记录里上传几张吧</div>';
            return;
        }

        photos.forEach(photo => {
            const item = document.createElement('article');
            item.className = 'gallery-admin-card';
            item.innerHTML = renderGalleryPhoto(photo);
            item.querySelector('[data-edit-source]').onclick = () => openMemoSource(photo.memo);
            list.appendChild(item);
        });
    } catch (e) {
        list.innerHTML = '<div class="empty-state">加载图库失败，请检查本地服务</div>';
    }
}

function renderGalleryPhoto(photo) {
    const memo = photo.memo;
    const date = formatMemoDate(memo.date);
    const privateBadge = memo.visibility === 'private' ? '<span class="memo-state private">私密</span>' : '';
    return `
        <a href="${escapeHtml(photo.src)}" target="_blank" rel="noopener noreferrer" class="gallery-admin-image">
            <img src="${escapeHtml(photo.src)}" alt="">
        </a>
        <div class="gallery-admin-info">
            <div class="gallery-admin-date">${escapeHtml(date)} ${privateBadge}</div>
            <div class="gallery-admin-desc">${escapeHtml(memo.content || '').slice(0, 54)}</div>
            <div class="gallery-admin-meta">
                ${memo.location ? `<span>${escapeHtml(memo.location)}</span>` : ''}
                <span>第 ${photo.index + 1} 张</span>
            </div>
            <button class="btn btn-secondary btn-icon" data-edit-source>编辑来源</button>
        </div>
    `;
}

function openMemoSource(memo) {
    const menuItem = document.querySelector('.menu-item[data-page="memos-page"]');
    switchPage('memos-page', menuItem);
    editMemo(memo);
}
