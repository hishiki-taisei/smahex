document.addEventListener('DOMContentLoaded', () => {
    const hexGrid = document.getElementById('hex-grid');
    const copyButton = document.getElementById('copy-button');
    const allowDuplicatesCheckbox = document.getElementById('allow-duplicates');
    const randomGenerateButton = document.getElementById('random-generate-button');
    const hiddenAllowDuplicatesInput = document.getElementById('hidden-allow-duplicates'); // hidden input取得

    // --- タッチデバイス判定 ---
    const isTouchDevice = ('ontouchstart' in window) || (navigator.maxTouchPoints > 0) || (navigator.msMaxTouchPoints > 0);

    // --- URL更新関数 (ランダム生成ボタンのみ更新) ---
    function updateRandomLink() {
        if (!randomGenerateButton || !allowDuplicatesCheckbox) return;

        const baseRandomUrl = randomGenerateButton.href.split('?')[0];
        const currentSize = new URL(randomGenerateButton.href).searchParams.get('size') || 'small';
        let randomUrlParams = new URLSearchParams({ size: currentSize });

        if (allowDuplicatesCheckbox.checked) {
            randomUrlParams.set('allow_duplicates', 'on');
        }
        randomGenerateButton.href = `${baseRandomUrl}?${randomUrlParams.toString()}`;
    }

    // --- Hidden Input 更新関数 ---
    function updateHiddenInput() {
        if (hiddenAllowDuplicatesInput && allowDuplicatesCheckbox) {
            hiddenAllowDuplicatesInput.value = allowDuplicatesCheckbox.checked ? 'on' : '';
        }
    }

    // --- イベントリスナー ---
    // チェックボックス変更時
    if (allowDuplicatesCheckbox) {
        allowDuplicatesCheckbox.addEventListener('change', () => {
            updateRandomLink(); // ランダム生成リンクを更新
            updateHiddenInput(); // hidden inputを更新
        });
    }

    // --- 初期化 ---
    updateRandomLink(); // ページ読み込み時にランダム生成リンクを初期化

    // --- マスのクリック処理 ---
    if (hexGrid) {
        hexGrid.addEventListener('click', (event) => {
            const clickedCell = event.target.closest('.hex-cell'); // クリックされたセル
            if (!clickedCell) return;

            // --- クリックフィードバック (タッチデバイスでない場合のみ、クリックされたセルのみ) ---
            if (!isTouchDevice) {
                clickedCell.classList.add('clicked');
                setTimeout(() => {
                    clickedCell.classList.remove('clicked');
                }, 150);
            }

            // --- 色変更処理 ---
            const currentState = clickedCell.classList.contains('state-red') ? 'red' :
                                 clickedCell.classList.contains('state-blue') ? 'blue' : 'default'; // デフォルト状態を示すように変更
            let nextStateClass = null; // 次の状態クラス (nullはデフォルト色に戻す)
            const removeClasses = ['state-red', 'state-blue']; // 常に削除するクラス

            if (currentState === 'default') {
                nextStateClass = 'state-red'; // 次は赤
            } else if (currentState === 'red') {
                nextStateClass = 'state-blue'; // 次は青
            } else { // blue
                // 次はデフォルト色 (クラス削除のみでOK)
            }

            // --- 重複許可チェックと連動処理 ---
            if (allowDuplicatesCheckbox && allowDuplicatesCheckbox.checked) {
                const iconFilename = clickedCell.dataset.icon; // クリックされたセルのアイコンファイル名を取得
                if (iconFilename) {
                    // 同じアイコンを持つすべてのセルを取得
                    const matchingCells = hexGrid.querySelectorAll(`.hex-cell[data-icon="${iconFilename}"]`);
                    // マッチしたすべてのセルの色を更新
                    matchingCells.forEach(cell => {
                        cell.classList.remove(...removeClasses); // 赤と青を削除
                        if (nextStateClass) { // 次が赤か青の場合
                            cell.classList.add(nextStateClass);
                        }
                        // nextStateClassがnullの場合はクラス削除のみ。
                        // これによりCSSの data-duplicates に基づくスタイルが適用される。
                    });
                } else {
                    // data-iconがない場合(念のため)、クリックされたセルのみ更新
                    clickedCell.classList.remove(...removeClasses);
                    if (nextStateClass) {
                        clickedCell.classList.add(nextStateClass);
                    }
                }
            } else {
                // 重複許可でない場合は、クリックされたセルのみ更新 (従来通り)
                clickedCell.classList.remove(...removeClasses);
                if (nextStateClass) {
                    clickedCell.classList.add(nextStateClass);
                }
            }
            // --- ここまで変更 ---
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