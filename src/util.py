from typing import List

def get_duplicate_indexes(lst:List[str]):
    """
    リスト内の同じ要素が3回以上出現する全てのインデックスをタプルとして返す関数

    この関数は、与えられたリスト内で3回以上出現する全ての要素のインデックスを探し、
    それらのインデックスをタプルの形でリストにまとめて返します。
    各タプルは、特定の要素が出現する全てのインデックスを含みます。

    Parameters:
        lst (list): 検索対象のリスト

    Returns:
        list of tuple: 同じ要素が3回以上出現する全てのインデックスを含むタプルのリスト
    """
    seen = {}
    # 各要素の全てのインデックスを記録
    for index, item in enumerate(lst):
        if item not in seen:
            seen[item] = [index]
        else:
            seen[item].append(index)

    # 3つ以上出現する要素のインデックスをタプルとしてまとめる
    return [tuple(indexes) for indexes in seen.values() if len(indexes) >= 2]

if __name__ == "__main__":
    # リスト内の同じ要素が3回以上出現する例
    my_list = ['as', 'b', 'c', 'a', 'd', 'as', 'caa', 'caa', 'cb']
    print(get_duplicate_indexes(my_list))
    
    my_list = ['a', 'b', 'c', 'd']
    print(get_duplicate_indexes(my_list))