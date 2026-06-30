// 网站发布

async function runDeploy() {
    const btn = document.getElementById('deploy-btn');
    const consoleDiv = document.getElementById('console');

    btn.disabled = true;
    btn.innerText = '正在推送部署中...';
    consoleDiv.innerText = '🚀 开始执行 Git 一键同步推送...\n';

    try {
        const data = await apiRequest('/api/deploy', { method: 'POST' });
        if (data.status === 'success') {
            consoleDiv.innerText += data.log + '\n\n✨ 部署推送流程执行完成！请在 GitHub Actions 查看运行情况！';
            showToast('代码部署推送成功！');
        } else {
            consoleDiv.innerText += '❌ 失败了: ' + data.message;
            showToast('部署失败！', true);
        }
    } catch (e) {
        consoleDiv.innerText += '❌ 网络连接或服务错误。';
        showToast('网络错误，执行失败', true);
    } finally {
        btn.disabled = false;
        btn.innerText = '🚀 立即推送部署上线';
    }
}

function initDeploy() {
    document.getElementById('deploy-btn').addEventListener('click', runDeploy);
}
