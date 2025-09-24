import os
import random
from flask import Flask, render_template, request, redirect, url_for, abort
from urllib.parse import quote, unquote
import time
from collections import Counter # collections.Counter をインポート

app = Flask(__name__)

# --- 定数定義 ---
ICON_FOLDER = os.path.join(app.static_folder, 'sma_icon')

# 盤面サイズ定義
BOARD_CONFIGS = {
    'small': {
        'display_name': '5x5', # 表示名を追加
        'grid_size': 25,
        'rows': [1, 2, 3, 4, 5, 4, 3, 2, 1]
        
        #'grid_size': 19,
        #'rows': [1, 2, 3, 2, 3, 2, 3, 2, 1]
    },
    'medium': {
        'display_name': '6x6', # 表示名を追加
        'grid_size': 36,
        'rows': [1, 2, 3, 4, 5, 6, 5, 4, 3, 2, 1]
        #'grid_size': 30,
        #'rows': [1, 2, 3, 4, 3, 4, 3, 4, 3, 4, 3, 2, 1]

    },
    'large': {
        'display_name': '7x7', # 表示名を追加
        'grid_size': 49,
        'rows': [1, 2, 3, 4, 5, 6, 7, 6, 5, 4, 3, 2, 1]
        #'grid_size': 43,
        #'rows': [1, 2, 3, 4, 5, 4, 5, 4, 5, 4, 3, 2, 1]
    },
    # --- 8x8 サイズを追加 ---
    'xlarge': {
        'display_name': '8x8',
        'grid_size': 64, # 1+2+...+7+8+7+...+1 = 64
        'rows': [1, 2, 3, 4, 5, 6, 7, 8, 7, 6, 5, 4, 3, 2, 1]
        #'grid_size': 58, # 1+2+...+7+8+7+...+1 = 64
        #'rows': [1, 2, 3, 4, 5, 6, 5, 6, 5, 6, 5, 4, 3, 2, 1]
    }
    # --- ここまで追加 ---
}
# 利用可能なサイズの順序付きリスト
AVAILABLE_SIZES = list(BOARD_CONFIGS.keys()) # ['small', 'medium', 'large', 'xlarge']

DEFAULT_BOARD_SIZE = 'small'
MAX_ICONS_NEEDED = max(config['grid_size'] for config in BOARD_CONFIGS.values())

# --- Helper Functions ---
def get_all_icons():
    """sma_iconフォルダからアイコンファイル名のリストを取得（ソート済み）"""
    try:
        icons = [f for f in os.listdir(ICON_FOLDER) if os.path.isfile(os.path.join(ICON_FOLDER, f))]
        icons.sort()
        if len(icons) < MAX_ICONS_NEEDED:
            print(f"警告: アイコンフォルダ ({ICON_FOLDER}) 内のアイコンが {MAX_ICONS_NEEDED} 個未満です。")
            return None # 最大サイズに必要な数がない場合はNoneを返す
        return icons
    except FileNotFoundError:
        print(f"エラー: アイコンフォルダが見つかりません: {ICON_FOLDER}")
        return None

all_icons_list = get_all_icons()

def generate_icons_from_seed(seed_value, grid_size, allow_duplicates=False): # allow_duplicates 引数を追加
    """指定されたSeed値とサイズに基づいてアイコンリストを生成する"""
    if all_icons_list is None:
        return None

    # 必要なアイコン数チェック (重複を許可しない場合のみ)
    if not allow_duplicates and len(all_icons_list) < grid_size:
         print(f"エラー: 指定されたサイズ({grid_size})に対してアイコン数が不足しています。")
         return None
    # 重複許可の場合は全アイコンリストが空でなければOK
    if allow_duplicates and not all_icons_list:
         print(f"エラー: アイコンリストが空です。")
         return None

    try:
        random.seed(seed_value)
        if allow_duplicates:
            # 重複を許可する場合: リストから重複ありで grid_size 個選択
            selected_icons = random.choices(all_icons_list, k=grid_size)
        else:
            # 重複を許可しない場合 (従来通り)
            shuffled_icons = list(all_icons_list)
            random.shuffle(shuffled_icons)
            selected_icons = shuffled_icons[:grid_size]
        return selected_icons
    except Exception as e:
        print(f"Seedからのアイコン生成中にエラー: {e}")
        return None

def generate_icons_with_handicap(seed_value, grid_size):
    """重複許可前提のハンデモード: 5個/4個/3個重複を必ず含める。
    戻り値: (icons_list, cell_labels) もしくは (None, None)
    """
    if all_icons_list is None or len(all_icons_list) < 3:
        print("エラー: ハンデモードに必要なアイコン数が不足しています。")
        return None, None

    required_total = 5 + 4 + 3
    if grid_size < required_total:
        print(f"エラー: 盤面サイズ({grid_size})がハンデ要件({required_total})を満たしません。")
        return None, None

    try:
        random.seed(seed_value)
        # 3種のアイコンを選定（重複しないように）
        base_icons = random.sample(all_icons_list, 3)
        icon5, icon4, icon3 = base_icons[0], base_icons[1], base_icons[2]

        # 各グループに付与するバッジ（同一グループ内は同じラベル）
        # 等確率で「ラベルなし（空文字）」も候補に含め、重複はしない
        badge_pool = ["ジャ禁", "シ禁", "A禁", "B禁"]
        selected_badges = random.sample(badge_pool, 3)
        badge5, badge4, badge3 = selected_badges[0], selected_badges[1], selected_badges[2]

        pairs = []  # (icon, label)
        pairs.extend([(icon5, badge5)] * 5)
        pairs.extend([(icon4, badge4)] * 4)
        pairs.extend([(icon3, badge3)] * 3)

        remaining = grid_size - len(pairs)
        # 残りは、上記3種を除外したプールから重複ありでランダム選択
        pool = [i for i in all_icons_list if i not in {icon5, icon4, icon3}]
        if not pool:
            pool = list(all_icons_list)
        if remaining > 0:
            rest_icons = random.choices(pool, k=remaining)
            pairs.extend([(icon, "") for icon in rest_icons])

        # ペアの順序をシャッフルし、iconsとlabelsに分解
        random.shuffle(pairs)
        icons = [icon for icon, _ in pairs]
        cell_labels = [label for _, label in pairs]
        return icons, cell_labels
    except Exception as e:
        print(f"ハンデモードのアイコン生成中にエラー: {e}")
        return None, None

# --- Routes ---
@app.route('/')
def home():
    """
    初回アクセス時にランダムなSeed値を生成し、
    デフォルトサイズで盤面を表示する/viewにリダイレクト
    """
    random_seed = random.randint(1000, 9999)
    # デフォルトサイズ(small)でリダイレクト（初期状態は ON にする）
    return redirect(url_for('view_board', seed=random_seed, size=DEFAULT_BOARD_SIZE, allow_duplicates='on'))

@app.route('/random')
def random_generate():
    """
    現在のサイズと重複設定を維持したまま、新しいランダムSeedで盤面を再生成する
    """
    current_size = request.args.get('size', DEFAULT_BOARD_SIZE).lower()
    if current_size not in BOARD_CONFIGS:
        current_size = DEFAULT_BOARD_SIZE

    # 重複許可フラグを取得（明示指定を優先、未指定時はFalse）
    _allow_param = request.args.get('allow_duplicates', None)
    allow_duplicates_flag = (_allow_param == 'on') if _allow_param is not None else False
    # ハンデモードフラグを取得（重複ON時のみ有効）
    handicap_up_flag = request.args.get('handicap_up') == 'on'

    random_seed = random.randint(1000, 9999)
    # リダイレクトURLに allow_duplicates を追加
    redirect_params = {'seed': random_seed, 'size': current_size}
    if allow_duplicates_flag:
        redirect_params['allow_duplicates'] = 'on'
        if handicap_up_flag:
            redirect_params['handicap_up'] = 'on'

    return redirect(url_for('view_board', **redirect_params))

@app.route('/view')
def view_board():
    """
    URLパラメータからSeed値、サイズ、重複設定を受け取り、盤面を表示する
    """
    seed_str = request.args.get('seed', None)
    current_size_key = request.args.get('size', DEFAULT_BOARD_SIZE).lower()
    # 重複許可フラグを取得（明示指定を優先、未指定時はFalse）
    _allow_param = request.args.get('allow_duplicates', None)
    allow_duplicates_flag = (_allow_param == 'on') if _allow_param is not None else False
    # ハンデモード（重複前提）
    handicap_up_flag = request.args.get('handicap_up') == 'on'

    # sizeパラメータが不正な場合はデフォルトにフォールバック
    if current_size_key not in BOARD_CONFIGS:
        current_size_key = DEFAULT_BOARD_SIZE

    if not seed_str:
        # リダイレクト時にも allow_duplicates を引き継ぐ
        redirect_params = {'size': current_size_key}
        if allow_duplicates_flag:
             redirect_params['allow_duplicates'] = 'on'
        return redirect(url_for('random_generate', **redirect_params))

    try:
        current_seed = int(seed_str)
    except ValueError:
        abort(400, description="Seed値は数字である必要があります。")

    # 現在のサイズ設定を取得
    current_config = BOARD_CONFIGS[current_size_key]
    grid_size = current_config['grid_size']
    row_config = current_config['rows']
    current_display_name = current_config['display_name'] # 現在の表示名

    # Seed値と重複/ハンデ設定を使ってアイコンリストを生成
    cell_labels = None
    if allow_duplicates_flag and handicap_up_flag:
        selected_icons, cell_labels = generate_icons_with_handicap(current_seed, grid_size)
    else:
        selected_icons = generate_icons_from_seed(current_seed, grid_size, allow_duplicates=allow_duplicates_flag)

    if selected_icons is None:
        # アイコンリスト自体がない場合と、数が足りない場合でメッセージを分ける
        if all_icons_list is None:
             error_msg = f"エラー: アイコンリストの読み込みに失敗しました。フォルダ({ICON_FOLDER})を確認してください。"
        else:
             error_msg = f"エラー: アイコンの生成に失敗しました。アイコン数({len(all_icons_list)})が指定サイズ({grid_size})に対して不足しています。"
        return error_msg, 500

    # --- アイコンの出現回数をカウント (重複許可の場合のみ) ---
    icon_counts = {}
    if allow_duplicates_flag and selected_icons:
        icon_counts = Counter(selected_icons)
    # --- ここまで追加 ---

    # 共有用のURL (allow_duplicates/handicap_up を含む)
    share_url_params = {'seed': current_seed, 'size': current_size_key, '_external': True}
    if allow_duplicates_flag:
        share_url_params['allow_duplicates'] = 'on'
        if handicap_up_flag:
            share_url_params['handicap_up'] = 'on'
    share_url = url_for('view_board', **share_url_params)

    # --- 全サイズの切り替え情報を生成 (allow_duplicates を含む) ---
    size_options = {}
    for size_key in AVAILABLE_SIZES:
        config = BOARD_CONFIGS[size_key]
        url_params = {'seed': current_seed, 'size': size_key}
        if allow_duplicates_flag:
            url_params['allow_duplicates'] = 'on'
            if handicap_up_flag:
                url_params['handicap_up'] = 'on'
        size_options[size_key] = {
            'display_name': config['display_name'],
            'url': url_for('view_board', **url_params),
            'is_active': size_key == current_size_key
        }

    return render_template(
        'index.html',
        icons=selected_icons,
        share_url=share_url,
        current_seed=current_seed,
        current_size_key=current_size_key, # 内部的なキー
        current_display_name=current_display_name, # 表示用の名前
        grid_size=grid_size,
        row_config=row_config,
        size_options=size_options, # 全サイズの情報を渡す
        allow_duplicates=allow_duplicates_flag, # テンプレートに渡す (チェックボックスの初期状態用)
        icon_counts=icon_counts, # アイコンカウント辞書を渡す
        handicap_up=handicap_up_flag,
        cell_labels=cell_labels or []
    )

if __name__ == '__main__':
    if all_icons_list is None:
        print(f"エラー: アイコンリストを読み込めませんでした。必要なアイコン数: {MAX_ICONS_NEEDED}。アイコンフォルダ({ICON_FOLDER})を確認してください。アプリケーションを終了します。")
    elif len(all_icons_list) < MAX_ICONS_NEEDED:
         print(f"警告: アイコン数が最大盤面サイズ({MAX_ICONS_NEEDED})に対して不足しています({len(all_icons_list)}個)。一部の盤面サイズでエラーが発生する可能性があります。")
         app.run(debug=True) # 警告は出すが、起動は試みる
    else:
        app.run(debug=True)