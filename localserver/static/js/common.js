// 通用工具与共享 UI 函数

function escapeHtml(str) {
    return String(str == null ? '' : str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

function showToast(msg, isError = false) {
    const toast = document.getElementById('toast');
    toast.innerText = msg;
    toast.style.backgroundColor = isError ? 'var(--danger-color)' : 'var(--success-color)';
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 3000);
}

function openModal(id) {
    document.getElementById(id).classList.add('active');
}

function closeModal(id) {
    document.getElementById(id).classList.remove('active');
}

// 统一的 JSON 请求封装，集中处理网络错误
async function apiRequest(url, options = {}) {
    const res = await fetch(url, options);
    return res.json();
}
