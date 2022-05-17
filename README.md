# FinalCheck - Blender Addon
日本語版は下にあります。/ Japanese version below.
## NO MORE Rendering Failures!
This addon detects problems in your project and make your render successful.

[Download From Here](https://github.com/omine-me/FinalCheck/releases)

![Screenshot on the addon](./README_fig1.png "Screenshot on the addon")  
A list of problematic items appears.

## About
Do you ever have to re-render your scene because of a small mistake?
This addon detects various problems of your project and suggest corrections.
Check with a single button and make it more efficient.

### Environment
#### Compatible Blender Versions
* Blender 2.90 or later

#### Languages
* English, Japanese

## Installation
#### Download
Download a .zip file from [here](https://github.com/omine-me/FinalCheck/releases).
#### Installation
Install the addon from Edit -> Preferences... -> Add-ons -> Install...  
You don't have to extract zip file.

## Usage
1. Open Sidebar in 3D Viewport.
2. In FinalCheck Panel, hit Check button.
3. A list of problematic items appears.
In Preferences sub-panel, you can toggle which items will be checked. These preferences are saved automatically.

### Checking Statuses  
* **Collections Visibility**: Does visibility of collections in viewports and renders differ? (Check based on eye, monitor, and, camera's icon.)
* **Objects Visibility**: Does visibility of objects in viewports and renders differ? (Check based on eye, monitor, and, camera's icon.)
* **Missing Files**: Is an image path broken? (Ignore packed file's path.)
* **Render Region**: Is render region set and the area reduced?
* **Resolution%**: Is resolution% under 100%?
* **Samples**: Is render samples under preview samples?
* **Instancing**: Does visibility of instancer in viewports and renders differ?
* **Modifiers**: Does visibility of modifiers in viewports and renders differ?
* **Composite** (alpha version): Do inputs of viewer node and composite node differ?  
Composite checking is currently incomplete due to limitations of the Blender Python API.
* **Particles: Show Emitter**: Does Visibility of particle emitter in viewports and renders differ?
* **Particles: Child Amount**: Does child amount of particles in viewports and renders differ?
* **Particles: Viewport Display Amount**: Is amount of particles in viewports under 100%?
* **Grease Pencil: Modifiers**: Does visibility of modifiers in viewports and renders differ?
* **Grease Pencil: Effects**: Does visibility of effects in viewports and renders differ?  

You can also choose where to check: all scenes or current scene/view_layer only.

## FAQ
**Q**: **Render result is not what I intended**  
**A**: This addon does not detect all problems. Check is based on current frame and does not consider status of other frames.  

**Q**: **Check takes a long time**  
**A**: Complex file may take longer to check. Try to decrease check items from preference. Checking image paths on network locations may also take time.  

## Feedback
If you find bugs or have an improvement, let me know in issues or my [Twitter](https://twitter.com/mineBeReal).
Thanks for using FinalCheck.

## License
Distributed under the MIT License.

---
## レンダリングの失敗をなくそう！
このアドオンは、Blenderファイルの問題を検出し、レンダリングを一発で成功させます。

[ダウンロードはここから](https://github.com/omine-me/FinalCheck/releases)

![アドオンのスクリーンショット](./README_fig1.png "アドオンのスクリーンショット")  
問題がある思われる項目が一覧で表示されます。

## はじめに
ほんの小さなミスで時間のかかるレンダリングをやり直すこと、ありますよね。  
このアドオンを使えば、ファイルの問題を見つけ出し、簡単に修正できます。  
ボタン一つで制作を効率化しましょう。

### 環境
#### 利用可能なBlenderのバージョン
* Blender 2.90 以降

#### 言語
* 日本語, 英語

## インストール
#### ダウンロード
[ここ](https://github.com/omine-me/FinalCheck/releases)からzipファイルをダウンロードします。
#### インストール
編集 -> プリファレンス... -> アドオン -> インストール... からインストールします。
zipファイルを展開する必要はありません。

## 使い方
1. 3D ビューポートでサイドパネルを開きます。
2. FinalCheckパネルからチェックボタンを押します。
3. 問題がある思われる項目が一覧で表示されます。
プリファレンスサブパネルから、チェックする項目を設定できます。これらは自動で保存されます。

### チェックする項目 
* **コレクションの可視性**: ビューポートとレンダーでコレクションの可視性が異なるか。(目のアイコン、モニターのアイコン、カメラのアイコンから判別します。)
* **オブジェクトの可視性**: ビューポートとレンダーでオブジェクトの可視性が異なるか。(目のアイコン、モニターのアイコン、カメラのアイコンから判別します。)
* **パスが不明なファイル**: 画像ファイルのパスが壊れているか。(パックされたファイルのパスはチェックしません。)
* **レンダー領域**: レンダー領域が設定されていて、レンダー領域が縮小しているか。
* **解像度%**: 解像度%が100%より小さいか。
* **サンプル数**: レンダーのサンプル数がビューポートのサンプル数より小さいか。
* **インスタンス化**: ビューポートとレンダーでインスタンサーの可視性が異なるか。
* **モディファイア**: ビューポートとレンダーでモディファイアの可視性が異なるか。
* **コンポジット** (アルファ版): ビューアーノードとコンポジットノードのインプットが異なるか。  
コンポジットのチェックは、Blender Python APIの制約により現状不完全です。
* **パーティクル: エミッターを表示**: ビューポートとレンダーでエミッターの可視性が異なるか。
* **パーティクル: 子パーティクルの量**: ビューポートとレンダーで子パーティクルの量が異なるか。
* **パーティクル: パーティクルの表示率**: ビューポートでのパーティクルの表示率が100%より小さいか。
* **グリースペンシル: モディファイア**: ビューポートとレンダーでモディファイアの可視性が異なるか。
* **グリースペンシル: エフェクト**: ビューポートとレンダーでエフェクトの可視性が異なるか。

プリファレンスから、全てのシーンをチェックするか、現在のシーン/ビューレイヤーのみをチェックするかも選択できます。

## FAQ
**Q**: **チェックしたにもかかわらず、意図しないレンダリングになる**  
**A**: 本アドオンは全てのミスを発見するものではありません。また、チェックは現在のフレームを元に行われ、他のフレームの状態をチェックしません。

**Q**: **チェックに時間がかかる**  
**A**: 複雑なファイルだとチェックに時間がかかることがあります。プリファレンスからチェック項目を減らしてみてください。また、パスが不明なファイルをチェックする際にネットワーク上のパスがあると、時間がかかることがあります。  

## フィードバック
バグやご意見は、issuesや[ツイッター](https://twitter.com/mineBeReal)からお願いします。
改善案も歓迎です。

## ライセンス
MITライセンスの下で利用可能です。
