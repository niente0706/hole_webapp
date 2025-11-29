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
HOLEの実装では(おそらく)厳格なPDBのフォーマットに従って原子名の先頭を読んで原子種を決めているようで、4文字以上の原子名では原子を正しく読み込めないようです。特に、4文字表記の原子名の2文字目が数字のような例ではHOLEが
```
***ERROR***
 Cannot find vdW radius for atom:
```
と言って止まってしまい、streamlit内の処理で
```
KeyError: 0
Traceback:
File "/path/to/hole_webapp/src/hole_webapp.py", line 152, in <module>
    pore_axis = hole_output[0].rxn_coord
```
というエラーが表示されます。
このような場合には読み込むPDBに対して事前に`src/rename_shorter.py`を使って原子名を3文字に変えておいてください。
>>>>>>> Stashed changes
