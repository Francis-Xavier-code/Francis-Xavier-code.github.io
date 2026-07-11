document.addEventListener('DOMContentLoaded', () => {
    document.querySelector('[data-action="open-new-post"]')
        .addEventListener('click', () => openModal('new-post-modal'));
    document.querySelector('[data-action="close-new-post"]')
        .addEventListener('click', () => {
            closeModal('new-post-modal');
            document.getElementById('new-post-form').reset();
        });
    document.getElementById('new-post-form').addEventListener('submit', submitNewPost);
    initDeploy();
    loadPosts();
});
