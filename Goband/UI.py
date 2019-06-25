#!/usr/bin/env python 
# -*- coding:utf-8 -*-
# import numpy as np

import GameEngine as GE


class GobangUI:

    Enum_GridStatus = {
        0: 'WhiteChess',
        1: 'BlackChess',
        2: 'Empty'
    }

    def __init__(self):
        return

    def PrintChessBoard(self, ChessBoardNP):
        for i in range(0, 2 * ChessBoardNP[0].__len__() + 2):
            print('-', end='')
        print()
        for CBRow in ChessBoardNP:
            print("|", end='')
            for i in range(0, CBRow.__len__()):
                if self.Enum_GridStatus[CBRow[i]] == 'WhiteChess':
                    print("O ", end='')
                elif self.Enum_GridStatus[CBRow[i]] == 'BlackChess':
                    print("X ", end='')
                else:
                    print("  ", end='')
            print('|')
        for i in range(0, 2 * ChessBoardNP[0].__len__() + 2):
            print('-', end='')
        print()
        return


def GetActionLocation(PlayerIndex, ActionStrBuff):
    RowNum = 0
    ColNum = 0
    for index in range(0, ActionStrBuff.__len__()):
        if ActionStrBuff[index] == ' ':
            RowNum = int(ActionStrBuff[0:index])
            ColNum = int(ActionStrBuff[index + 1:])
            break

    return GE.GobangAction(RowNum, ColNum, PlayerIndex)


def ChessBoardAction(RuleEngine, ChessBoard, NowAction):
    if not RuleEngine.CheckGameEnd(NowAction, ChessBoard):
        if ChessBoard[NowAction.ActionPoint_Row][NowAction.ActionPoint_Col] == 2:
            ChessBoard[NowAction.ActionPoint_Row][NowAction.ActionPoint_Col] = NowAction.ActionIndex
        else:
            return "此处已有棋子"
    else:
        if NowAction.ActionIndex == 0:
            return "白子获胜"
        else:
            return "黑子获胜"
    return "OK"


def main():
    NewUI = GobangUI()
    NewRuleEngine = GE.GobangRuleEngine()

    CB = []
    for i in range(0, 7):
        Row = []
        for j in range(0, 7):
            Row.append(2)
        CB.append(Row)

    NowPlayer = "Black"
    while True:
        if NowPlayer == "Black":
            print("黑子落子：")
            PlayerIndex = 1
        else:
            print("白子落子：")
            PlayerIndex = 0
        ActionStr = input()
        NowAction = GetActionLocation(PlayerIndex, ActionStr)

        HintStr = ChessBoardAction(NewRuleEngine, CB, NowAction)
        if HintStr != "OK":
            print(HintStr)
            continue

        if NowPlayer == "Black":
            NowPlayer = "White"
        else:
            NowPlayer = "Black"

        NewUI.PrintChessBoard(CB)


main()
