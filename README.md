# hole_webapp
This is a repository for a web application that provides a GUI for the HOLE program. This app allows users to run HOLE calculations and visualize the results (pore radius plots and 3D structure) directly in the browser, powered by MDAnalysis and Streamlit.

## 目的
- HOLEをGUIから触れるようにしたい
- 結果を別のアプリケーション(gnuplotなどでのプロット、vmdなどでのポアの位置確認)を使わずにすぐに確認したい

## 内容
streamlitによるwebアプリに以下の機能を実装する。
- HOLEオプション確認GUI
- PDBファイル選択機能
- HOLE実行ボタン
- 半径プロット機能とプロットした画像保存機能
- 結果確認用3Dビューワー

## 使うもの
- [streamlit](https://streamlit.io)
- [MDAnalysis](https://www.mdanalysis.org)
- [matplotlib](https://matplotlib.org)
- [stmol](https://github.com/napoles-uach/stmol)

## セットアップ
```bash
git clone https://github.com/niente0706/hole_webapp.git
cd hole_webapp
conda create env -f requirements.txt
conda activate hole_webapp
chmod +x run_hole_webapp
nohup ./run_hole_webapp &
```

## 終了方法
```bash
pgrep -f hole_webapp
# 出てきたプロセスIDをkill
kill xxxxx
```

## 注意点
### ログ機能は開発中
pythonの組み込みのロギング機能ではなぜかうまくログがファイルに記録されないようです。Streamlitは独自にロガーをもっているようなので、手が空き次第そちらを使って実装します。

### ファイルの文字数制限
PDBの名前(具体的には`./logs/YYYYMMDD_PDBNAME/PDBNAME.ext`)の文字数が長すぎる(70文字程度)を超えるとHOLEの仕様でパスがうまく読めなくなるのでエラーを吐きます。長すぎない名前に変えて再実行してください。

### 原子名の文字数制限
HOLEの仕様では原子名は3文字までしか許容されておらず、4文字の原子名をもつ原子を読み込む際に正しく原子種を読み込めない可能性があります。
このアプリでは4文字の原子名の原子は4文字目を除いた3文字の原子名に変換して処理しているので、出力されたPDBファイルでは原子名が変わっていることにご注意ください。
