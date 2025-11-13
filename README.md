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
- [NGLviewer](http://nglviewer.org)

## 使い方
1. サーバーホスト機で`run_hole_webapp`を実行する
2. localhost用とネットワーク用にURLが表示されるのでそれをコピーする
3. ブラウザからURLにアクセスする
