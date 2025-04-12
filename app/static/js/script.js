document.addEventListener('DOMContentLoaded', () => {
    const hexGrid = document.getElementById('hex-grid');
    const copyButton = document.getElementById('copy-button');
    const shareUrlInput = document.getElementById('share-url-input');
    const copyFeedback = document.getElementById('copy-feedback');

    // --- マスのクリック処理 ---
    if (hexGrid) {
        hexGrid.addEventListener('click', (event) => {
            // クリックされた要素が .hex-cell またはその子要素か確認
            const cell = event.target.closest('.hex-cell');
            if (!cell) return; // 関係ない場所をクリックした場合は何もしない

            // 現在の色状態を取得
            const currentState = cell.classList.contains('state-red') ? 'red' :
                                 cell.classList.contains('state-blue') ? 'blue' : 'white';

            // クラスを一旦すべて削除
            cell.classList.remove('state-white', 'state-red', 'state-blue');

            // 次の色状態を設定
            let nextStateClass;
            if (currentState === 'white') {
                nextStateClass = 'state-red';
            } else if (currentState === 'red') {
                nextStateClass = 'state-blue';
            } else { // blue or initial
                nextStateClass = 'state-white';
            }
            cell.classList.add(nextStateClass);
        });
    }

    // --- クリップボードコピー処理 ---
    if (copyButton && shareUrlInput) {
        copyButton.addEventListener('click', () => {
            shareUrlInput.select(); // テキストを選択状態にする (任意)
            shareUrlInput.setSelectionRange(0, 99999); // モバイル用

            navigator.clipboard.writeText(shareUrlInput.value)
                .then(() => {
                    // 成功時のフィードバック
                    copyFeedback.textContent = 'コピーしました！';
                    copyButton.textContent = 'コピー完了';
                    setTimeout(() => {
                        copyFeedback.textContent = '';
                        copyButton.textContent = 'クリップボードにコピー';
                    }, 2000); // 2秒後に元に戻す
                })
                .catch(err => {
                    // 失敗時のフィードバック
                    console.error('クリップボードへのコピーに失敗しました:', err);
                    copyFeedback.textContent = 'コピーに失敗しました';
                     setTimeout(() => {
                        copyFeedback.textContent = '';
                    }, 3000);
                });
        });
    }
});