document.addEventListener('DOMContentLoaded', () => {
    const hexGrid = document.getElementById('hex-grid');
    const copyButton = document.getElementById('copy-button');
    const allowDuplicatesCheckbox = document.getElementById('allow-duplicates'); // チェックボックス取得
    const randomGenerateButton = document.getElementById('random-generate-button'); // ランダム生成ボタン取得
    const seedForm = document.getElementById('seed-form'); // Seedフォーム取得
    const seedInput = document.getElementById('seed-input'); // Seed入力欄取得 (フォームアクション更新用)

    // --- タッチデバイス判定 ---
    const isTouchDevice = ('ontouchstart' in window) || (navigator.maxTouchPoints > 0) || (navigator.msMaxTouchPoints > 0);

    // --- URL更新関数 ---
    function updateLinks() {
        if (!randomGenerateButton || !seedForm || !seedInput || !allowDuplicatesCheckbox) return; // 要素がなければ何もしない

        const baseRandomUrl = randomGenerateButton.href.split('?')[0];
        const baseFormAction = seedForm.action.split('?')[0];
        const currentSize = new URL(randomGenerateButton.href).searchParams.get('size') || 'small'; // 現在のサイズ取得
        const currentSeed = seedInput.value; // 現在のSeed値取得

        let randomUrlParams = new URLSearchParams({ size: currentSize });
        let formActionParams = new URLSearchParams({ size: currentSize, seed: currentSeed }); // formにはseedも必要

        if (allowDuplicatesCheckbox.checked) {
            randomUrlParams.set('allow_duplicates', 'on');
            formActionParams.set('allow_duplicates', 'on');
        }

        randomGenerateButton.href = `${baseRandomUrl}?${randomUrlParams.toString()}`;
        // フォームのaction属性を直接書き換える
        seedForm.action = `${baseFormAction}?${formActionParams.toString()}`;
        // 注意: フォーム送信時にseedパラメータがURLとname属性で重複するが、通常はURLの値が優先されるか、
        // name属性の値で上書きされる。GETなので問題になりにくい。
        // より厳密には、送信直前にactionを書き換えるか、hidden inputを使う方法もある。
    }

    // --- イベントリスナー ---
    // チェックボックス変更時
    if (allowDuplicatesCheckbox) {
        allowDuplicatesCheckbox.addEventListener('change', updateLinks);
    }
    // Seed入力変更時 (フォームアクション更新のため)
    if (seedInput) {
         seedInput.addEventListener('input', updateLinks);
    }

    // --- 初期化 ---
    updateLinks(); // ページ読み込み時に初期状態を反映

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