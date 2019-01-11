# 工場IoT技術検証用　プロトタイプ開発
## 02. ラベル読み取り

### 概要
    テキスト、バーコード、刻印など何等かのマークを読み取りデジタル化

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
    OpenCV 3.1.0, NumPy, picamera

### ファイル構成
* 未定
* 刻印画像
* README.md             本ファイル

### 実行方法
（暫定）
1. RaspberryPiコンソールで、python3で実行する。
2. 文字列にカメラを向ける。
    * 検知した文字列上に認識した文字がオーバーライトされる。
3. 1次元バーコードにカメラを向ける。
    * 
2. 対象の刻印にカメラを向ける。
    * 対象刻印を検知すると、プレビュー画面の該当箇所に緑の矩形が表示される。
    * 別ウィンドウで検知した刻印を表示する。
3. プレビュー画面右上の「×」を押下して終了


### 動作概要

1. カメラ起動、プレビュー画像取得
2. 刻印検出
3. バーコード検出
4. テキスト検出


## 処理詳細

### 特徴点マッチングによる刻印検出

OpenCVの特徴量検出とマッチング機能を用いて、メーターの検出と画像補正を行う。
入力はカメラからのプレビュー画像、出力はプレビュー画像から切り抜いたメーター画像である。

#### 処理
1. 対象メータテンプレート画像の読み込み
2. AKAZEモデル生成、テンプレート画像の特徴量算出
3. カメラキャプチャ画像の特徴量算出
4. テンプレート画像とキャプチャ画像の特徴量比較・マッチング
5. 適合した特徴点からホモグラフィ変換行列を求める。(RANSAC)
6. ホモグラフィ変換行列からキャプチャ画像上のテンプレート画像領域を算出し、矩形を描画
7. ホモグラフィ変換の逆行列を算出し、キャプチャ画像からメーター画像を切り出す。

#### パラメータ
* カメラ解像度（640×480）
* ホモグラフィ変換のアルゴリズム（RANSAC）
* 特徴点のマッチング精度（距離が60%以下）
* 画像のマッチング精度（10以上特徴点がマッチングした場合）

#### 課題
* マッチング精度のチューニング（特徴点のマッチング基準と、画像のマッチングの基準）
* 検出時のFPS（検出機能を実行すると10分の1になる）
* 複数のメーターの同時検出
* 他の特徴量算出アルゴリズムを試す



### バーコード検出

### テキスト検出


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

Python+OpenCVのディープラーニング(CNN)でテキスト領域検出
https://ensekitt.hatenablog.com/entry/2018/06/15/200000
OpenCVでQRコード検出器を書く
http://iphone.moo.jp/app/?p=897