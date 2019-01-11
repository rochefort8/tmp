# 工場IoT技術検証用　プロトタイプ開発
## 03. 画像センシングによる異常検知

### 概要
	* タンク・ミキサーの表面をカメラで監視、液漏れ・ひび割れ等の異常があれば通知
	* 巻き取り器表面をカメラで監視、摩耗状態を画像認識
	* 水分、水滴の検知


### 開発環境・実行環境
* プラットフォーム
  Raspberry Pi 3 Model B
* カメラ
  Camera ver 2.1
* OS
  Raspbian Stretch with desktop and recommended software
	Version: November 2018	Kernel version:4.14

* 開発言語
    python 3.5
* ライブラリ
    OpenCV 3.1.0, NumPy, picamera, TensorFlow

### ファイル構成
* 未定
* README.md             本ファイル

### 実行方法
（暫定）
学習フェイズ
1. RaspberryPiコンソールで、python3で実行する。
2. 正常な画像を学習。


判定フェイズ
1. 対象にカメラを向ける。
2. 障害物を置く
	* 異常が発生した通知
	* 異常を検知した画像を表示する。
3. プレビュー画面右上の「×」を押下して終了


### 動作概要

学習フェイズ
1. カメラ起動、プレビュー画像取得
2.

判定フェイズ
1. カメラ起動、プレビュー画像取得
2.



## 処理詳細


-------------------------------------------------------------------------------
## 補足

### カメラのセットアップ

1. RaspberryPiにカメラを接続
2. 動作確認（デモ） => $ raspivid -d
3. Piccameraのインストール
    * OpenCVでは、RaspberryPiカメラを直接参照できない。（USBカメラはOK）
      pipでインストール + 
      $ pip install picamera
    * virtualenvを使用していて、パスが通っていない場合は以下のようにパスを通す。 +
      $ cd ~/.virtualenvs/cv-python3/lib/python3.5/site-packages + 
      $ ln /usr/lib/python3/dist-package/picamera  


### 参考URL
[OpenCV3とPython3で特徴点を抽出する]  
https://qiita.com/hitomatagi/items/62989573a30ec1d8180b

[いまさら局所特徴量で物体検出]  
https://qiita.com/hmichu/items/f5f1c778a155c7c414fd

[特徴点のマッチング]
http://labs.eecs.tottori-u.ac.jp/sd/Member/oyamada/OpenCV/html/py_tutorials/py_feature2d/py_matcher/py_matcher.html

Raspberry PiとTensorFlowを使ったディープラーニングの開発環境構築 
https://karaage.hatenadiary.jp/entry/2017/08/09/073000
