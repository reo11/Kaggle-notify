import subprocess
import requests
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

############ Set your params here ###########
JSON_FILE_NAME = "XXXXX.json"
SHEET_NAME = "XXXXX"
LINE_TOKEN = "XXXXXX"
COMPETITION_NAME = "santander-customer-transaction-prediction"

use_params = ["url", "title"]


def kaggle_kernels_api(competition):
    '''
    input: competiton name
    output: response of kaggle api
    Don't forget to set your kaggpe api token in ~/.kaggle
    '''
    cmd = "kaggle kernels list --competition {} --sort-by 'dateCreated'".format(competition)
    return subprocess.run(cmd, shell=True,stdout = subprocess.PIPE, stderr = subprocess.PIPE).stdout.decode("utf8")


def kernels(kernel_list):
    '''
    input: response of kaggle api
    output: kernels(dict)["url", "title"]
    '''
    kernels = []
    rows = kernel_list.split("\n")
    for i in range(len(rows )):
        # スペース2つでlist化
        row = rows[i].split("  ")
        # 先頭/末尾のスペースを削除
        row = [x.strip(" ") for x in row if x]
        kernels.append(row)
    # ヘッダとフッタを除外
    kernels = kernels[2:-1]
    # 古い順にする
    kernels = kernels[::-1]
    # dictに変える
    dict_kernels = [{} for i in range(len(kernels))]
    for i, kernel in enumerate(kernels):
        for j, param in enumerate(use_params):
            dict_kernels[i][param] = "https://kaggle.com/" + kernel[j] if param == "url" else kernel[j]
    return dict_kernels


def read_worksheet(json_file_name, sheet_name):
    '''
    input: json_file_name of service account key, google spread sheet name
    output: worksheet
    '''
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(json_file_name, scope)
    gc = gspread.authorize(credentials)
    wks = gc.open(sheet_name).sheet1
    return wks, gc

def line(message):
    '''
    input: Message, line notify api token
    '''
    line_notify_api = 'https://notify-api.line.me/api/notify'
    payload = {'message': '\n' + message}
    headers = {'Authorization': 'Bearer ' + LINE_TOKEN}
    line_notify = requests.post(line_notify_api, data=payload, headers=headers)


def main(wks, kernels, gc):
    wks_values = wks.get_all_values()

    # 新しく作る時(途中でエラーが起きるとバグる)
    if len(wks_values) == 0:
        update_list = wks.range('A2:{}{}'.format(chr(ord("A") + len(use_params) - 1), 1+len(kernels)))
        value_list = []
        for kernel in kernels:
            for param in use_params:
                value_list.append(kernel[param])
        for i, (cell, value) in enumerate(zip(update_list, value_list)):
            cell.value = value
        for i, param in enumerate(use_params):
            column = chr(ord("A") + i)
            wks.update_acell('{}1'.format(column), param)
        wks.update_cells(update_list)

        message = "スプレッドシートに新しいデータを追加しました\nhttps://docs.google.com/spreadsheets/d/{}".format(gc.open(SHEET_NAME).id)
        line(message)
    # 投稿が追加されているか確認
    elif wks_values[-1][1] != kernels[-1]["title"]:
        index = 0
        for i, kernel in enumerate(kernels):
            if wks_values[-1][1] == kernel["title"]:
                index = i
        new_kernels = kernels[index+1:]

        for kernel in new_kernels:
            message = "新しいカーネルが公開されました\n{}\n{}".format(kernel["title"], kernel["url"])
            line(message)

        value_list = []
        for kernel in new_kernels:
            for param in use_params:
                value_list.append(kernel[param])

        start = len(wks_values) + 1
        end = start + len(new_kernels) - 1
        update_list = wks.range('A{}:{}{}'.format(start, chr(ord("A") + len(use_params) - 1), end))

        for i, (cell, value) in enumerate(zip(update_list, value_list)):
            cell.value = value
        wks.update_cells(update_list)
    else:
        print("nothing to update")

if __name__ == '__main__':
    kernel_list = kaggle_kernels_api(COMPETITION_NAME)
    kernels = kernels(kernel_list)
    worksheet, gc = read_worksheet(JSON_FILE_NAME, SHEET_NAME)
    main(worksheet, kernels, gc)

