import os
import re
import sys
from typing import List
from unicodedata import normalize as uni_norm
from pathlib import Path

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    resource_dir = Path(sys._MEIPASS)
else:
    resource_dir = (Path(__file__).parent.parent / 'resource')

dict_path = resource_dir / 'open_jtalk_dic_utf_8-1.11'

# 環境変数'OPEN_JTALK_DICT_DIR'にresource_pathを設定
os.environ['OPEN_JTALK_DICT_DIR'] = str(dict_path)

import pyopenjtalk
import romkan

# 正規表現パターンのコンパイル
half_width_alphanumeric_pattern = re.compile(r'^[a-zA-Z0-9]+$')



def is_half_width_alphanumeric(s:str):
    """
    半角英数字かどうかを判定する関数

    この関数は、与えられた文字列が半角英数字のみで構成されているかどうかを判定します。
    半角英数字のみで構成されている場合はTrue、そうでない場合はFalseを返します。

    Parameters:
        s (str): 判定する文字列

    Returns:
        bool: 文字列が半角英数字のみで構成されている場合はTrue、そうでない場合はFalse
    """
    return bool(half_width_alphanumeric_pattern.match(s))

def trim_underscores(lst:List):
    """
    リストの先頭と末尾からアンダースコアと 'cl' を取り除く関数

    この関数は、与えられたリストの先頭と末尾にあるアンダースコア('_')と 'cl' を取り除きます。
    ただし、リストの中間にあるアンダースコアや 'cl' は取り除かれません。

    Parameters:
        lst (List): 処理するリスト

    Returns:
        List: 処理後のリスト
    """
    start = 0
    end = len(lst)
    while start < end and lst[start] in ("_", "cl"):
        start += 1
    while start < end and lst[end-1] in ("_", "cl"):
        end -= 1
    return lst[start:end]

def labels_to_phonemes(labels:List[str]):
    """
    フルコンテキストラベルから音素を抽出する関数
    
    この関数は、フルコンテキストラベルから音素を抽出します。
    フルコンテキストラベルは、音声合成システムで使用されるラベル形式で、
    音素情報の他に、アクセントや音高などの情報を含んでいます。
    この関数では、その中から音素情報のみを抽出して返します。

    Parameters:
        labels (List[str]): フルコンテキストラベル

    Returns:
        List: 抽出された音素
    """
    return [label.split("-")[1].split("+")[0].lower() for label in labels[1:-1]]

def replace_cl_with_consonant(phonemes:List):
    """
    リスト内の 'cl' を次の子音に置換する関数

    この関数は、与えられた音素のリスト内の 'cl' を、リスト内の次の音素に置換します。
    ただし、リストの末尾にある 'cl' は無視されます。

    Parameters:
        phonemes (List): 処理する音素のリスト

    Returns:
        List: 処理後の音素のリスト
    """
    replaced = []
    for i, phoneme in enumerate(phonemes):
        if phoneme == 'cl':
            # 末尾の 'cl' は無視する
            if i+1 < len(phonemes):
                replaced.append(phonemes[i+1][0])
        else:
            replaced.append(phoneme)
    return replaced

def jp2roma(text: str) -> str:
    """
    日本語のテキストをローマ字に変換する関数

    この関数は、与えられた日本語のテキストをローマ字に変換します。
    変換プロセスでは、まずpyopenjtalkを使用してテキストから音素を抽出し、
    その音素をローマ字にマッピングします。この関数では、特定の音素の処理、
    例えば、促音記号 'cl' の子音への置換や、音素リストの先頭と末尾の '_' または 'cl' の削除も行います。

    Parameters:
        text (str): 変換する日本語のテキスト

    Returns:
        str: ローマ字に変換されたテキスト
    """
    text = re.sub(r'[（(].*?[）)]', '', text)
    njd_features = pyopenjtalk.run_frontend(text)
    phonemes = []

    position = 0
    for feature in njd_features:
        string = uni_norm('NFKC', text[position:position+len(feature['string'])])
        if is_half_width_alphanumeric(string):
            phonemes.append(string)
        elif string == feature['string']:
            feature['pron'] = feature['read']
            labels = pyopenjtalk.make_label([feature])
            if labels:
                  phonemes.extend(labels_to_phonemes(labels))
            else:
                  phonemes.append('_')
        else:
          continue
        position += len(feature['string'])

    # 先頭と末尾の '_' または 'cl' を削除
    phonemes = trim_underscores(phonemes)

    # 促音記号 'cl' を子音に置換
    phonemes = replace_cl_with_consonant(phonemes)
    
    if phonemes:
        concatenated = ''.join(phonemes)
        if len(concatenated) > 40:
            concatenated = concatenated[:40] + '#'
        return concatenated
    else:
        raise ValueError(f"'{text}'は解析できない文章です")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("引数が足りません")
        sys.exit(1)

    input_dirpath = sys.argv[1]
    output_dirpath = sys.argv[2]
    audio_filepath_list = [Path(os.path.join(input_dirpath, file)) for file in sorted(os.listdir(input_dirpath)) if file.endswith('.wav') or file.endswith('.mp3')]
    new_name = [jp2roma(path.stem) for path in audio_filepath_list]
    
    for ap,nn in zip(audio_filepath_list,new_name):
        file_name = re.sub(r'[（(].*?[）)]', '', ap.stem)
        print(f"{file_name} -> {nn}")