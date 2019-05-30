#!/usr/bin/env python 
# -*- coding:utf-8 -*-
# import numpy as np


class GobandUI:

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
        return


def main():
    NewUI = GobandUI()

    CB = []
    for i in range(0, 7):
        Row = []
        for j in range(0, 7):
            Row.append(1)
        CB.append(Row)

    NewUI.PrintChessBoard(CB)


main()
