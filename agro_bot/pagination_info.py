from collection_editer import delete_information
from pagination_kb import create_pagination_keyboard
import pandas as pd


class DataFramePaginator:
    def __init__(self, df, page_number = 0):
        self.df = df.reset_index(drop=True)
        self.page_number = page_number

    def get_current_page(self):
        start_index = self.page_number
        end_index = (self.page_number + 1)
        return self.df.iloc[start_index:end_index]
    
    def get_page_number(self):
        return self.page_number
    
    def get_keyboard(self, editor_buttons = True, info = None):
        keyboard = None
        if (self.page_number + 1) >= len(self.df) and self.page_number <= 0:
            keyboard = create_pagination_keyboard(['Add'], editor_buttons=editor_buttons, info=info)
        elif (self.page_number + 1) >= len(self.df):
            keyboard = create_pagination_keyboard(['backward','Add'], editor_buttons=editor_buttons, info=info)
        elif self.page_number <= 0:
            keyboard = create_pagination_keyboard(['Add', 'forward'], editor_buttons=editor_buttons, info=info)
        else:
            keyboard = create_pagination_keyboard(['backward', 'Add', 'forward'], editor_buttons=editor_buttons, info=info)
        return keyboard
    
    def set_DataFrame(self, df):
        self.df = df.reset_index(drop=True)
    
    def increment_page(self):
        self.page_number += 1

    def decrement_page(self):
        self.page_number -= 1

    def get_DataFrame(self):
        return self.df
    
    def get_document_id(self):
        return str(self.df.loc[self.page_number, 'document_id'])
    
    def get_info(self, key):
        columns_name = self.df.columns.to_list()
        if key in columns_name:
            return self.df.loc[:, key].to_list()
        else:
            raise print('No such field')
        
    def del_info(self, key):
        self.df = delete_information(self.df, 'document_id', key)
        self.df = self.df.reset_index(drop=True)

    def __getitem__(self, key):
        idx = self.df['farmer_tg_id'].to_list()
        if key in idx:
            return self.df[self.df['farmer_tg_id'] == key]
        else:
            return pd.DataFrame()
