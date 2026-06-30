// 文章管理

async function loadPosts() {
    const list = document.getElementById('posts-list');
    try {
        const posts = await apiRequest('/api/posts');
        list.innerHTML = '';

        if (posts.length === 0) {
            list.innerHTML = '<div class="empty-state"><span class="empty-icon">📭</span>当前还没有任何文章，点击右上角新增一篇吧</div>';
            return;
        }

        posts.forEach(post => {
            const dateStr = post.date ? post.date.substring(0, 10) : '无日期';
            const badge = post.draft
                ? '<span class="badge badge-draft">草稿</span>'
                : '<span class="badge badge-pub">已发布</span>';
            const safeTitle = escapeHtml(post.title);
            const safeSlug = escapeHtml(post.slug);

            const row = document.createElement('div');
            row.className = 'list-row';
            row.innerHTML = `
                <div class="item-meta">
                    <div class="item-title" title="${safeTitle}">${safeTitle}</div>
                    <div class="item-subtitle">
                        <span>📅 ${dateStr}</span>
                        <span>📁 content/post/${safeSlug}</span>
                        ${badge}
                    </div>
                </div>
                <div class="actions">
                    <button class="btn btn-secondary btn-icon" data-edit="${safeSlug}">✒️ 编辑</button>
                    <button class="btn btn-danger btn-icon" data-delete="${safeSlug}">🗑️ 删除</button>
                </div>
            `;
            row.querySelector('[data-edit]').onclick = () => editPost(post.slug);
            row.querySelector('[data-delete]').onclick = () => deletePost(post.slug);
            list.appendChild(row);
        });
    } catch (e) {
        list.innerHTML = '<div class="empty-state">加载文章失败，请检查本地服务</div>';
    }
}

async function editPost(slug) {
    try {
        const data = await apiRequest(`/api/posts/edit/${encodeURIComponent(slug)}`, { method: 'POST' });
        if (data.status === 'success') {
            showToast('已成功唤起 Typora / 系统编辑器打开文章！');
        } else {
            showToast(data.message, true);
        }
    } catch (e) {
        showToast('网络错误，无法打开编辑器', true);
    }
}

async function deletePost(slug) {
    if (!confirm(`确认要彻底删除文章 [${slug}] 吗？此操作无法恢复！`)) return;
    try {
        const data = await apiRequest(`/api/posts/${encodeURIComponent(slug)}`, { method: 'DELETE' });
        if (data.status === 'success') {
            showToast('文章删除成功！');
            loadPosts();
        } else {
            showToast(data.message, true);
        }
    } catch (e) {
        showToast('网络错误，删除失败', true);
    }
}

async function submitNewPost(e) {
    e.preventDefault();
    const title = document.getElementById('post-title-input').value;
    const slug = document.getElementById('post-slug-input').value;
    const description = document.getElementById('post-desc-input').value;

    try {
        const data = await apiRequest('/api/posts', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, slug, description }),
        });
        if (data.status === 'success') {
            showToast('文章创建成功！即将自动唤起编辑器...');
            closeModal('new-post-modal');
            document.getElementById('new-post-form').reset();
            loadPosts();
            setTimeout(() => editPost(data.slug), 1000);
        } else {
            showToast(data.message, true);
        }
    } catch (err) {
        showToast('网络错误，创建失败', true);
    }
}
