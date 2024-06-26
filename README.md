## 概要
- キャラクターの画像を3Dオブジェクト化するための便利な機能を集めたアドオンです。
- パーツごとの画像をインポートして、最終的に1つのオブジェクトとして統合するところまでできます。
- Blenderの標準addonであるImport Image as Planesなどと併用するのがオススメ。
##  各機能解説
### Toggle Wireframe
- 選択したオブジェクトの、ワイヤーフレーム表示をon/offする。
- onとoffが混ざっている場合は、いったんoffになる。
### Order Layer
- レイヤー分けしたいオブジェクトを、1_◯◯、2_◯◯というように、下のレイヤーから1から順にCollectionの上から順になるように名前をつける。
(この時点では数字が順番になってなくてもいい)<br>
※Blenderでは、名前の順番にCollectionが並ぶので、この手順は必要になります。一番下になるレイヤーがコレクションの上から並ぶようにrenameしてください。

- レイヤー分けしたいオブジェクトをすべて選択する
- layer offsetに、各レイヤーの距離を指定する(0.0001がおすすめ)。
- Oeder Layerを押すと、Layerを整列させることができる。(y軸方向に整列させる)
### Rename Layer
- オブジェクトの名前に、1から順に名前のprefixをつけるようにrenameされる。
- すでにあるprefixは削除されるので注意してください。
- Collectionでレイヤー順に並んでいるとしても、スクリプトが判断できない場合があるので、この手順は必ず行ってください。
### Square UV Pack
- 選択したオブジェクトを、正方形の範囲に収まるようにUV展開&Packします。　
- UV.squareというUVMapが自動生成されます。
- Bake Textureという、正方形の画像が自動で作成されます。
  - image-sizeで、Bake Texutreのサイズを指定してください。
  - rotate partsをチェックすると、効率よくpackされますが、Normalなど自作したい場合はチェックしないほうがいいかもしれません。
  - pack marginは、各パーツ間のmarginを設定できます。
  - ※上記2つは、Pack Islandしたときに設定できる項目と同一です。
### Bake Texture
- 選択したオブジェクトを、上記で作成されたBake Textureにベイクします。
- マシンパワーがけっこういるかもしれないです。また、かなり時間がかかります。
### Set Material
- 選択したオブジェクトに対して、ベイクしたテクスチャに置き換えて新しいマテリアル「character」を作成します。
- 不必要になった元のUVMapを削除します。
### Create Vertex Group
- 選択したオブジェクトから、オブジェクト名と同名の頂点グループを作成し、アサインします。
- これは、オブジェクトが統合された際に頂点の選択が大変になるので、あらかじめ統合前のオブジェクトの頂点情報を保存する意味で作成しています。
- 不必要であればこの手順は飛ばしてもかまいません。
### Integrate Objects
- 選択したオブジェクトを統合して、1つのオブジェクトにします。