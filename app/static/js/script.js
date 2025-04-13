document.addEventListener('DOMContentLoaded', () => {
    const hexGrid = document.getElementById('hex-grid');
    const copyButton = document.getElementById('copy-button');
    // const shareUrlInput = document.getElementById('share-url-input'); // 削除
    // const copyFeedback = document.getElementById('copy-feedback'); // 削除

    // --- マスのクリック処理 ---
    if (hexGrid) {
        hexGrid.addEventListener('click', (event) => {
            // クリックされた要素が .hex-cell またはその子要素か確認
            const cell = event.target.closest('.hex-cell');
            if (!cell) return; // 関係ない場所をクリックした場合は何もしない

            // --- クリックフィードバック ---
            cell.classList.add('clicked');
            // アニメーションが終わる頃にクラスを削除
            setTimeout(() => {
                cell.classList.remove('clicked');
            }, 150); // CSSのtransition時間より少し短くても良い
            // --- ここまで追加 ---

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
    if (copyButton) {
        copyButton.addEventListener('click', () => {
            const urlToCopy = copyButton.dataset.shareUrl; // data属性からURLを取得
            if (!urlToCopy) {
                console.error('コピーするURLが見つかりません。');
                return;
            }

            navigator.clipboard.writeText(urlToCopy) // 取得したURLを使用
                .then(() => {
                    // 成功時のフィードバック (ボタンテキスト変更のみ)
                    copyButton.textContent = 'コピー完了';
                    copyButton.classList.add('copied');

                    setTimeout(() => {
                        copyButton.textContent = 'URLをコピー';
                        copyButton.classList.remove('copied');
                    }, 2000);
                })
                .catch(err => {
                    // 失敗時のフィードバック (コンソール出力のみ)
                    console.error('クリップボードへのコピーに失敗しました:', err);
                });
        });
    }
});