import os
import random
from flask import Flask, render_template, request, redirect, url_for, abort
from urllib.parse import quote, unquote
import time

app = Flask(__name__)

# --- 定数定義 ---
ICON_FOLDER = os.path.join(app.static_folder, 'sma_icon')

# 盤面サイズ定義
BOARD_CONFIGS = {
    'small': {
        'display_name': '5x5', # 表示名を追加
        'grid_size': 25,
        'rows': [1, 2, 3, 4, 5, 4, 3, 2, 1]
    },
    'medium': {
        'display_name': '6x6', # 表示名を追加
        'grid_size': 36,
        'rows': [1, 2, 3, 4, 5, 6, 5, 4, 3, 2, 1]
    },
    'large': {
        'display_name': '7x7', # 表示名を追加
        'grid_size': 49,
        'rows': [1, 2, 3, 4, 5, 6, 7, 6, 5, 4, 3, 2, 1]
    },
    # --- 8x8 サイズを追加 ---
    'xlarge': {
        'display_name': '8x8',
        'grid_size': 64, # 1+2+...+7+8+7+...+1 = 64
        'rows': [1, 2, 3, 4, 5, 6, 7, 8, 7, 6, 5, 4, 3, 2, 1]
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

def generate_icons_from_seed(seed_value, grid_size):
    """指定されたSeed値とサイズに基づいてアイコンリストを生成する"""
    if all_icons_list is None:
        return None
    if len(all_icons_list) < grid_size: # 要求されたサイズのアイコン数があるか再確認
         print(f"エラー: 指定されたサイズ({grid_size})に対してアイコン数が不足しています。")
         return None

    try:
        random.seed(seed_value)
        shuffled_icons = list(all_icons_list)
        random.shuffle(shuffled_icons)
        # 要求されたグリッドサイズ分のアイコンを返す
        selected_icons = shuffled_icons[:grid_size]
        return selected_icons
    except Exception as e:
        print(f"Seedからのアイコン生成中にエラー: {e}")
        return None

# --- Routes ---
@app.route('/')
def home():
    """
    初回アクセス時にランダムなSeed値を生成し、
    デフォルトサイズで盤面を表示する/viewにリダイレクト
    """
    random_seed = random.randint(1000, 9999)
    # デフォルトサイズ(small)でリダイレクト
    return redirect(url_for('view_board', seed=random_seed, size=DEFAULT_BOARD_SIZE))

# --- 新しいランダム生成ルートを追加 ---
@app.route('/random')
def random_generate():
    """
    現在のサイズを維持したまま、新しいランダムSeedで盤面を再生成する
    """
    # クエリパラメータから現在のサイズを取得、なければデフォルト
    current_size = request.args.get('size', DEFAULT_BOARD_SIZE).lower()
    if current_size not in BOARD_CONFIGS:
        current_size = DEFAULT_BOARD_SIZE

    random_seed = random.randint(1000, 9999)
    # 受け取ったサイズと新しいSeedでリダイレクト
    return redirect(url_for('view_board', seed=random_seed, size=current_size))
# --- ここまで追加 ---

@app.route('/view')
def view_board():
    """
    URLパラメータからSeed値とサイズを受け取り、盤面を表示する
    """
    seed_str = request.args.get('seed', None)
    current_size_key = request.args.get('size', DEFAULT_BOARD_SIZE).lower() # 内部的なキー

    # sizeパラメータが不正な場合はデフォルトにフォールバック
    if current_size_key not in BOARD_CONFIGS:
        current_size_key = DEFAULT_BOARD_SIZE

    if not seed_str:
        # seedがない場合は /random ルートにリダイレクトして処理させる
        # (現在のサイズを引き継ぐため)
        return redirect(url_for('random_generate', size=current_size_key))

    try:
        current_seed = int(seed_str)
    except ValueError:
        abort(400, description="Seed値は数字である必要があります。")

    # 現在のサイズ設定を取得
    current_config = BOARD_CONFIGS[current_size_key]
    grid_size = current_config['grid_size']
    row_config = current_config['rows']
    current_display_name = current_config['display_name'] # 現在の表示名

    # Seed値を使ってアイコンリストを生成
    selected_icons = generate_icons_from_seed(current_seed, grid_size)

    if selected_icons is None:
        # アイコンリスト自体がない場合と、数が足りない場合でメッセージを分ける
        if all_icons_list is None:
             error_msg = f"エラー: アイコンリストの読み込みに失敗しました。フォルダ({ICON_FOLDER})を確認してください。"
        else:
             error_msg = f"エラー: アイコンの生成に失敗しました。アイコン数({len(all_icons_list)})が指定サイズ({grid_size})に対して不足しています。"
        return error_msg, 500

    # 共有用のURL (seedとsizeを含む)
    share_url = url_for('view_board', seed=current_seed, size=current_size_key, _external=True)

    # --- 全サイズの切り替え情報を生成 ---
    size_options = {}
    for size_key in AVAILABLE_SIZES:
        config = BOARD_CONFIGS[size_key]
        size_options[size_key] = {
            'display_name': config['display_name'],
            'url': url_for('view_board', seed=current_seed, size=size_key),
            'is_active': size_key == current_size_key
        }
    # --- ここまで追加 ---

    return render_template(
        'index.html',
        icons=selected_icons,
        share_url=share_url,
        current_seed=current_seed,
        current_size_key=current_size_key, # 内部的なキー
        current_display_name=current_display_name, # 表示用の名前
        grid_size=grid_size,
        row_config=row_config,
        size_options=size_options # 全サイズの情報を渡す
    )

if __name__ == '__main__':
    if all_icons_list is None:
        print(f"エラー: アイコンリストを読み込めませんでした。必要なアイコン数: {MAX_ICONS_NEEDED}。アイコンフォルダ({ICON_FOLDER})を確認してください。アプリケーションを終了します。")
    elif len(all_icons_list) < MAX_ICONS_NEEDED:
         print(f"警告: アイコン数が最大盤面サイズ({MAX_ICONS_NEEDED})に対して不足しています({len(all_icons_list)}個)。一部の盤面サイズでエラーが発生する可能性があります。")
         app.run(debug=True) # 警告は出すが、起動は試みる
    else:
        app.run(debug=True)