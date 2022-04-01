# wordle_solver
平均情報量を用いてwordleにおける最善手を提案します。
下のHPを参考に作成しました。
https://qiita.com/masaka_programming/items/2afe7aa86edb85f19741

wordle_local.py: ローカル環境で最適します。  
wordle_lambda.py: AWSのlambdaで実行します。大量にやるとお金かかるからやりすぎないでね。

使い方
1. 実行すると、最適な単語を提案されます。 例："suggested word is tares"  

2. "input your word :" と訊かれるので、wordleに実際に入力した単語を入力します。 例： tares  
   空白で(何も打たず)enterを押しても大丈夫です。その場合、直前に提案された単語を入力したとみなします。  
   
3. 続けて、"input its response :"と訊かれるので、wordleからの返答を入力します。  
   緑色はo(小文字のオー)、黄色は-(半角のバー)、灰色はx(小文字のエックス)で記載します。例： xo-xx  
   
4. プログラムから、正解としてありうる単語のリストと、次に入力すべき単語が提案されます。　例："suggested word is robin"  
 
5. 1~4を続けていき、候補としてありうる単語が一つに絞られたら"the answer is XXXXX"と表示され、終了します。
