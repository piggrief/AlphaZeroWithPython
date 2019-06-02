#!/usr/bin/env python 
# -*- coding:utf-8 -*-


class GobangAction:

    ActionPoint_Row = 0
    ActionPoint_Col = 0
    ActionIndex = 0      # 0代表落白子，1代表落黑子，2代表不落子

    def __init__(self, Row, Col, Index):
        """
        构造行动信息。
        :param Row: 落子行
        :param Row: 落子列
        :Index Row: 落子操作
        """
        self.ActionPoint_Row = Row
        self.ActionPoint_Col = Col
        self.ActionIndex = Index
        return


class GobangRuleEngine:
    """
    五子棋规则引擎类
    """
    ChessBoardSize = 7

    def __init__(self):
        return

    def CheckGameEnd(self, NowAction, ChessBoard):
        """
        检测游戏是否结束
        :param NowAction: 当前行动
        :param ChessBoard: 要被检测的棋盘，类型是列表的列表
        """

        Row = NowAction.ActionPoint_Row
        Col = NowAction.ActionPoint_Col
        ChessIndex = NowAction.ActionIndex

        ColIndex = Col - 1
        ChessNum = 0
        Flag_QuitWhile = False
        # 行左扫
        while not Flag_QuitWhile:
            if ColIndex < 0:
                break
            else:
                if ChessBoard[Row][ColIndex] == ChessIndex:
                    ChessNum = ChessNum + 1
                else:
                    Flag_QuitWhile = True

                ColIndex = ColIndex - 1
        ColIndex = Col + 1
        Flag_QuitWhile = False
        # 行右扫
        while not Flag_QuitWhile:
            if ColIndex >= self.ChessBoardSize:
                break
            else:
                if ChessBoard[Row][ColIndex] == ChessIndex:
                    ChessNum = ChessNum + 1
                else:
                    Flag_QuitWhile = True

                ColIndex = ColIndex + 1

        if ChessNum >= 4:
            return True

        RowIndex = Row - 1
        ChessNum = 0
        Flag_QuitWhile = False
        # 列上扫
        while not Flag_QuitWhile:
            if RowIndex < 0:
                break
            else:
                if ChessBoard[RowIndex][Col] == ChessIndex:
                    ChessNum = ChessNum + 1
                else:
                    Flag_QuitWhile = True

                RowIndex = RowIndex - 1
        RowIndex = Row + 1
        Flag_QuitWhile = False
        # 列下扫
        while not Flag_QuitWhile:
            if RowIndex >= self.ChessBoardSize:
                break
            else:
                if ChessBoard[RowIndex][Col] == ChessIndex:
                    ChessNum = ChessNum + 1
                else:
                    Flag_QuitWhile = True

                RowIndex = RowIndex + 1

        if ChessNum >= 4:
            return True

        RowIndex = Row - 1
        ColIndex = Col - 1
        ChessNum = 0
        Flag_QuitWhile = False
        # ↖扫
        while not Flag_QuitWhile:
            if RowIndex < 0 or ColIndex < 0:
                break
            else:
                if ChessBoard[RowIndex][ColIndex] == ChessIndex:
                    ChessNum = ChessNum + 1
                else:
                    Flag_QuitWhile = True

                RowIndex = RowIndex - 1
                ColIndex = ColIndex - 1
        RowIndex = Row + 1
        ColIndex = Col + 1
        Flag_QuitWhile = False
        # ↘扫
        while not Flag_QuitWhile:
            if RowIndex >= self.ChessBoardSize or ColIndex >= self.ChessBoardSize:
                break
            else:
                if ChessBoard[RowIndex][ColIndex] == ChessIndex:
                    ChessNum = ChessNum + 1
                else:
                    Flag_QuitWhile = True

                RowIndex = RowIndex + 1
                ColIndex = RowIndex + 1

        if ChessNum >= 4:
            return True

        RowIndex = Row - 1
        ColIndex = Col + 1
        ChessNum = 0
        Flag_QuitWhile = False
        # ↗扫
        while not Flag_QuitWhile:
            if RowIndex < 0 or ColIndex >= self.ChessBoardSize:
                break
            else:
                if ChessBoard[RowIndex][ColIndex] == ChessIndex:
                    ChessNum = ChessNum + 1
                else:
                    Flag_QuitWhile = True

                RowIndex = RowIndex - 1
                ColIndex = ColIndex + 1
        RowIndex = Row + 1
        ColIndex = Col - 1
        Flag_QuitWhile = False
        # ↙扫
        while not Flag_QuitWhile:
            if RowIndex >= self.ChessBoardSize or ColIndex < 0:
                break
            else:
                if ChessBoard[RowIndex][ColIndex] == ChessIndex:
                    ChessNum = ChessNum + 1
                else:
                    Flag_QuitWhile = True

                RowIndex = RowIndex + 1
                ColIndex = ColIndex - 1

        if ChessNum >= 4:
            return True

        return False
