// 入口：页面导航与初始化

const PAGE_TITLES = {
    'posts-page': '文章管理',
    'memos-page': '瞬间记录',
    'gallery-page': '图库预览',
    'photos-page': '图片管理',
    'deploy-page': '网站发布',
};

function switchPage(pageId, menuItem) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.menu-item').forEach(m => m.classList.remove('active'));

    document.getElementById(pageId).classList.add('active');
    menuItem.classList.add('active');
    document.getElementById('page-title').innerText = PAGE_TITLES[pageId] || '';

    if (pageId === 'posts-page') loadPosts();
    if (pageId === 'memos-page') loadMemos();
    if (pageId === 'gallery-page') loadGallery();
    if (pageId === 'photos-page') loadPhotos();
}

function initNavigation() {
    document.querySelectorAll('.menu-item').forEach(item => {
        item.addEventListener('click', () => switchPage(item.dataset.page, item));
    });
}

function initPostsUI() {
    document.querySelector('[data-action="open-new-post"]')
        .addEventListener('click', () => openModal('new-post-modal'));
    document.querySelector('[data-action="close-new-post"]')
        .addEventListener('click', () => {
            closeModal('new-post-modal');
            document.getElementById('new-post-form').reset();
        });
    document.getElementById('new-post-form').addEventListener('submit', submitNewPost);
}

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initPostsUI();
    initMemos();
    initPhotos();
    initDeploy();
    loadPosts();
});
