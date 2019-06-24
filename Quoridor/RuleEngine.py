#!/usr/bin/env python 
# -*- coding:utf-8 -*-
import numpy as np
import copy


class Point:
    def __init__(self, X_Set=0, Y_Set=0):
        self.X = X_Set
        self.Y = Y_Set


class Grid:
    """
    棋格类
    """
    GridStatus = 0  # 0 代表棋格位位空，1代表有白子，2代表有黑子
    IfUpBoard = False  # 棋格上方是否有横挡板
    IfLeftBoard = False  # 棋格左方是否有竖挡板

    def __init__(self, GridStatus_Set=0, IfUpBoard_Set=False, IfLeftBoard_Set=False):
        """
        构造函数
        :param GridStatus_Set:格子状态
        :param IfUpBoard_Set:是否有上挡板
        :param IfLeftBoard_Set:是否有左挡板
        """
        self.GridStatus = GridStatus_Set
        self.IfUpBoard = IfUpBoard_Set
        self.IfLeftBoard = IfLeftBoard_Set
        return


class ChessBoard:
    """
    棋盘类
    """
    def __init__(self):
        """
        初始化棋盘状态
        """
        self.ChessBoardAll = np.zeros([7, 7], dtype=Grid)
        for i in range(0, self.ChessBoardAll.shape[0]):
            for j in range(0, self.ChessBoardAll.shape[1]):
                self.ChessBoardAll[i, j] = Grid(self)
        self.ChessBoardAll[0, 3].GridStatus = 1
        self.ChessBoardAll[6, 3].GridStatus = 2
        self.Player1Location = Point(-1, -1)
        self.Player2Location = Point(-1, -1)
        self.NumPlayer1Board = 16
        self.NumPlayer2Board = 16
        return

    @staticmethod
    def DrawNowChessBoard(ChessBoardNow):
        """
        绘制棋盘
        :return:
        """
        for i in range(0, ChessBoardNow.ChessBoardAll.shape[0] * 2):
            rowindex = i // 2
            for j in range(0, ChessBoardNow.ChessBoardAll.shape[1] * 2):
                colindex = j // 2
                if i % 2 == 0:  # 横档板显示行
                    if ChessBoardNow.ChessBoardAll[rowindex, colindex].IfUpBoard:
                        print("\033[31m─\033[0m", end='')
                    else:
                        print("─", end='')
                else:
                    if j % 2 == 0:  # 竖挡板显示列
                        if ChessBoardNow.ChessBoardAll[rowindex, colindex].IfLeftBoard:
                            print("\033[31m|\033[31m", end='')
                        else:
                            print("|", end='')
                    else:
                        if ChessBoardNow.ChessBoardAll[rowindex, colindex].GridStatus == 1:  # 白子
                            print("⚪", end='')
                        elif ChessBoardNow.ChessBoardAll[rowindex, colindex].GridStatus == 2:  # 黑子
                            print("●", end='')
                        else:
                            print(" ", end='')
            print()
        print()

    @staticmethod
    def SaveChessBoard(ChessBoardNow):
        """
        保存棋盘至返回值
        :param ChessBoardNow: 待保存的棋盘
        :return: 保存后的棋盘
        """
        ChessBoardSave = copy.deepcopy(ChessBoardNow)
        return ChessBoardSave

    @staticmethod
    def ResumeChessBoard(ChessBoardSave):
        """
        恢复棋盘至返回值
        :param ChessBoardSave: 保存的棋盘
        :return: 待恢复的棋盘
        """
        ChessBoard_Resumed = copy.deepcopy(ChessBoardSave)
        return ChessBoard_Resumed


class QuoridorRuleEngine:
    """
    Quoridor游戏规则引擎类
    """
    def __init__(self):
        return

    @staticmethod
    def CheckGameResult(ChessBoardToCheck):
        if ChessBoardToCheck.Player1Location.X == 6:
            return "P1 Success"
        elif ChessBoardToCheck.Player2Location.X == 0:
            return "P2 Success"
        else:
            return "No Success"

