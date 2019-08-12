#!/usr/bin/env python 
# -*- coding:utf-8 -*-
import xlrd
import numpy as np
import copy


class ChessManual:

    def __init__(self):
        self.ManualData = []
        self.TrainData = []
        return

    def Read(self, filename):
        """
        棋谱读取程序，filename得是一个excel文件的位置，读出的棋谱被保存在ManualData内
        :param filename: 一个excel文件的位置
        :return: 无
        """
        WorkBook = xlrd.open_workbook(filename=filename)
        Sheet1 = WorkBook.sheet_by_index(0)
        RowIndex = 0
        self.ManualData = []
        while True:
            Row = Sheet1.row_values(RowIndex, 1)
            if Row[0] == "End":
                break
            else:
                RowIndex += 1
            # region 解算行信息成动作序列
            for i in range(Row.__len__()):
                if Row[i] == "End":
                    del Row[i:]
                    break
            self.ManualData.append(Row)
            # endregion

    def ManualToTrainData(self):
        """
        从类的棋谱数据(ManualData)转换成类的训练数据(TrainData)
        :return: 无
        """
        for OnceGameData in self.ManualData:
            OnceGameData = list(OnceGameData)
            states = []
            states_renew = np.zeros((4, 7, 7))
            states_renew[2, 0, 3] = 1
            states_renew[3, 6, 3] = 1
            P1Location_Row = 0
            P1Location_Col = 3
            P2Location_Row = 6
            P2Location_Col = 3
            ToSaveStates = copy.deepcopy(states_renew)
            states.append(ToSaveStates)

            mcts_probs = []
            winner_z = np.zeros(len(OnceGameData) - 1)
            WinnerPlayer = OnceGameData[0]
            for i in range(1, OnceGameData.__len__()):
                # region 初始化一条训练数据的三个成分列表
                move_probs = np.zeros((4, 7 * 7))
                # endregion
                ActionNum = int(OnceGameData[i] // 100)
                ActionRow = int((OnceGameData[i] // 10) % 10)
                ActionCol = int(OnceGameData[i] % 10)
                # region 更新move_probs
                LocationBuff = ActionRow * 7 + ActionCol
                move_probs[ActionNum, LocationBuff] = 1
                mcts_probs.append(move_probs)
                # endregion
                # region 更新states
                if ActionNum == 2:  # 移动P1
                    states_renew[2, P1Location_Row, P1Location_Col] = 0
                    states_renew[2, ActionRow, ActionCol] = 1
                    P1Location_Row = ActionRow
                    P1Location_Col = ActionCol
                elif ActionNum == 3:  # 移动P2
                    states_renew[3, P2Location_Row, P2Location_Col] = 0
                    states_renew[3, ActionRow, ActionCol] = 1
                    P2Location_Row = ActionRow
                    P2Location_Col = ActionCol
                elif ActionNum == 0:  # 竖挡板
                    states_renew[0, ActionRow, ActionCol] = 1
                    states_renew[0, ActionRow + 1, ActionCol] = 1
                elif ActionNum == 1:  # 横挡板
                    states_renew[1, ActionRow, ActionCol] = 1
                    states_renew[1, ActionRow, ActionCol + 1] = 1
                ToSaveStates = copy.deepcopy(states_renew)
                states.append(ToSaveStates)
                # endregion
                # region 更新winner_z
                if i % 2 == 1:  # P1动作
                    if WinnerPlayer == 1:
                        winner_z[i - 1] = 1
                    else:
                        winner_z[i - 1] = -1
                if i % 2 == 0:  # P2动作
                    if WinnerPlayer == 2:
                        winner_z[i - 1] = 1
                    else:
                        winner_z[i - 1] = -1
                # endregion
            del states[len(states) - 1]
            play_data = zip(states, mcts_probs, winner_z)
            play_data = list(play_data)[:]
            self.TrainData.extend(play_data)


if __name__ == '__main__':
    CM = ChessManual()
    CM.Read("D:\智能车\步步为营人工智障\AlphaZeroWithPython\AlphaZeroWithPython\ChessMannal\CM.xls")
    CM.ManualToTrainData()
    print(len(CM.TrainData))
    asd = input()
    print(asd)
