from pathlib import Path
from shutil import copy2

import customtkinter
from CTkMessagebox import CTkMessagebox
import romkan

from jp2roma import jp2roma


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("jp2roma_v1.0")
        self.geometry("400x150")
        self.grid_columnconfigure(0,weight=1)
        
        # dirpath input form
        self.input_dirpath_frame = PathFormFrame(self,placeholder_text="音声ファイルがあるフォルダを指定してください")
        self.input_dirpath_frame.grid(row=0,column=0,padx=10,pady=10,sticky="ew")
        self.output_dirpath_frame = PathFormFrame(self,placeholder_text="出力先のフォルダをしていしてください")
        self.output_dirpath_frame.grid(row=1,column=0,padx=10,pady=10,sticky="ew")
        
        # init
        self.input_dirpath = ""
        self.outpout_dirpath = ""
        
        # execute
        self.execute_button = customtkinter.CTkButton(self,text="実行",command=self.execute)
        self.execute_button.grid(row=2,column=0,padx=40,pady=10)
        
    def path_exist_check(self):
        """
        入力パスと出力パスの存在をチェックする関数

        この関数は、ユーザーが指定した入力パスと出力パスが実際に存在するかどうかをチェックします。
        どちらか一方でも存在しない場合は、エラーメッセージを表示し、Falseを返します。

        Returns:
            bool: 両方のパスが存在する場合はTrue、そうでない場合はFalse
        """
        if not self.input_dirpath.exists(): 
            msg = CTkMessagebox(
                title="エラー:フォルダが見つかりませんでした",
                message=f"音声フォルダ\n\n{self.input_dirpath}\n\nが存在しません。\n\n存在するフォルダのパスを指定してください。",
                icon="cancel",
                sound=True
            )
            return False
        if not self.output_dirpath.exists():
            msg = CTkMessagebox(
                title="エラー:フォルダが見つかりませんでした",
                message=f"出力先フォルダ\n\n{self.output_dirpath}\n\nが存在しません。\n\n存在するフォルダのパスを指定してください。",
                icon="cancel",
                sound=True
                
            )
            return False
        
        return True
            
    
    def path_empty_check(self):
        """
        パスが空かどうかをチェックする関数

        この関数は、入力パスと出力パスが空かどうかをチェックし、
        どちらかが空の場合は警告メッセージを表示します。

        Returns:
            bool: パスが空でない場合はTrue、空の場合はFalse
        """
        print(self.input_dirpath)
        print(self.output_dirpath)
        if self.input_dirpath == "" or self.output_dirpath == "":
            msg = CTkMessagebox(
                title="警告",
                message="フォルダのパスを指定してください",
                icon="info",
                sound=True
            )
            return False
        
        return True
        
    def path_duplicatioin_warning(self):
        """
        パスの重複をチェックする関数

        この関数は、入力パスと出力パスが重複しているかどうかをチェックします。
        重複している場合は警告メッセージを表示し、ユーザーに続行の選択を促します。

        Returns:
            bool: パスが重複していない場合はTrue、重複している場合はFalse
        """
        print(self.input_dirpath)
        print(self.output_dirpath)
        if self.input_dirpath == self.output_dirpath:
            msg = CTkMessagebox(
                title="警告",
                message="音声フォルダと出力先フォルダが重複しています！\n\n続行してもよろしいですか？",
                icon="warning",
                option_1="続行",
                option_2="キャンセル",
                sound=True
            )
            if msg.get() == "キャンセル":
                return False
        
        return True
    
    def confirm(self):
        """
        ユーザーに出力先の確認を促す関数

        この関数は、ユーザーにリネーム後の音声ファイルが指定された出力フォルダに保存されることを確認します。
        ユーザーが「はい」を選択した場合、関数はTrueを返し、処理が続行されます。
        「キャンセル」を選択した場合、関数はFalseを返し、処理が中断されます。

        Returns:
            bool: ユーザーが「はい」を選択した場合はTrue、それ以外の場合はFalse
        """
        msg = CTkMessagebox(
            title="確認",
            message=f"リネーム音声を以下のフォルダに出力します。\n\n{self.output_dirpath}\n\nよろしいですか？",
            option_1="はい",
            option_2="キャンセル",
            sound=True
        )
        return True if msg.get() == "はい" else False
            
    def execute(self):
        self.input_dirpath = self.input_dirpath_frame.get()
        self.output_dirpath = self.output_dirpath_frame.get()
        
        # check and execute
        if self.path_empty_check() and self.path_exist_check() and self.path_duplicatioin_warning() and self.confirm():
            audio_filepath_list = [file for file in self.input_dirpath.iterdir() if file.suffix == '.wav' or file.suffix == '.mp3']
            try:
                new_stems = [jp2roma(path.stem) for path in audio_filepath_list]
                with open(self.output_dirpath/'log.txt','w') as f:
                    for origin,new_stem in zip(audio_filepath_list,new_stems):
                        romkan_string = romkan.to_hiragana(new_stem)
                        
                        origin_padding = ''.join(['　']*(20 - len(origin.stem)))
                        new_stem_padding = ''.join([' ']*(40 - len(new_stem)))
                        romkan_padding = ''.join(['　']*(20 - len(romkan_string)))
                        f.write(f"{origin.stem}{origin_padding} -> {new_stem}{new_stem_padding} -> {romkan_string}{romkan_padding}\n")
                        copy2(origin.resolve(),self.output_dirpath / (new_stem+origin.suffix))
            except ValueError as e:
                msg = CTkMessagebox(
                    title="変換に失敗しました",
                    message=e.__str__(),
                    icon='cancel',
                    sound=True
                )
                
            
                
            msg = CTkMessagebox(
                title="完了！",
                message="変換が完了しました！",
                sound=True
            )
                
        else:
            return False
        

class PathFormFrame(customtkinter.CTkFrame):
    """
    このクラスは、パスの入力欄と、参照ボタンを提供します。

    Attributes:
        master (customtkinter.CTk): 親ウィジェット
        placeholder_text (str): エントリのプレースホルダーテキスト
        filepath (str): ファイルパスを保持する変数
        path_enter (customtkinter.CTkEntry): 入力ディレクトリパスを入力するエントリ
        reference_button (customtkinter.CTkButton): ディレクトリを参照するためのボタン
    """
    def __init__(self,master:customtkinter.CTk,placeholder_text:str = ""):
        
        super().__init__(master)
        
        self.grid_columnconfigure(0,weight=4)
        
        self.path_enter = customtkinter.CTkEntry(self,placeholder_text=placeholder_text)
        self.path_enter.grid(row=0,column=0,sticky="ew")
        self.reference_button = customtkinter.CTkButton(self,text="参照",width=80,command=self.open_directory_dialog)
        self.reference_button.grid(row=0,column=1)
        
    
    def open_directory_dialog(self):
        path = customtkinter.filedialog.askdirectory()
        current_val = self.path_enter.get()
        self.path_enter.delete(0,len(current_val))
        self.path_enter.insert(0,path)
    
    def get(self):
        if self.path_enter.get() != "":
            return Path(self.path_enter.get().strip('"')).resolve()
        else:
            return ""
        
if __name__ == "__main__":
    app = App()
    app.mainloop()