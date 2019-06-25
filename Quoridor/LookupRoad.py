#!/usr/bin/env python 
# -*- coding:utf-8 -*-


class Point:
    def __init__(self, X_Set=0, Y_Set=0):
        self.X = X_Set
        self.Y = Y_Set


class LookupRoadAlgorithm:
    class AstarList:
        def __init__(self, HH, GG, FF, row, col, Father_set=1):
            self.H = HH
            self.G = GG
            self.F = FF
            self.Grid_row = row
            self.Grid_col = col
            self.Father = Father_set

    Min_DistanceLength = 0
    Astar_Stop = False
    Player1MinRoad = []
    Player2MinRoad = []

    def AstarRestart(self, ToAstarSearch, Player, Location_row, Location_col):
        self.Min_DistanceLength = 999
        self.Astar_Stop = False
        InitGrid = self.AstarList(6, 0, 6, Location_row, Location_col)
        InitAList = []
        InitAList.append(InitGrid)
        distance = self.LookupRoad_Astar(ToAstarSearch, Player, InitGrid, 1, [], InitAList)
        return self.Min_DistanceLength

    def LookupRoad_Astar(self, ThisChessBoard, Player, NowGrid, num_renew, OpenList, CloseList):
        if self.Astar_Stop:
            return self.Min_DistanceLength
        Location_row = NowGrid.Grid_row
        Location_col = NowGrid.Grid_col
        if Player == 0:  # P1白子
            Row_Destination = 6
        elif Player == 1:  # P2黑子
            Row_Destination = 0
        else:
            Row_Destination = 0

        # region 检查四周能移动的位置添加进P_List_Enable列表
        P_List_Enable = []
        # 左
        if Location_col > 0 and (not ThisChessBoard.ChessBoardAll[Location_row, Location_col].IfLeftBoard):
            P_List_Enable.append(Point(Location_row, Location_col - 1))
        # 右
        if Location_col < 6 and (not ThisChessBoard.ChessBoardAll[Location_row, Location_col + 1].IfLeftBoard):
            P_List_Enable.append(Point(Location_row, Location_col + 1))
        # 上
        if Location_row > 0 and (not ThisChessBoard.ChessBoardAll[Location_row, Location_col].IfUpBoard):
            P_List_Enable.append(Point(Location_row - 1, Location_col))
        # 下
        if Location_row < 6 and (not ThisChessBoard.ChessBoardAll[Location_row + 1, Location_col].IfUpBoard):
            P_List_Enable.append(Point(Location_row + 1, Location_col))
        # endregion

        # region 上下扫描是否有木板，用来减少搜索空间
        flag_NoBoard = True
        flag_UpNowBoard = True
        flag_DownNowBoard = True

        for k in range(Location_row + 1, Row_Destination + 1):
            if ThisChessBoard.ChessBoardAll[k, Location_col].IfUpBoard:
                flag_DownNowBoard = False
                break
        for k in range(Location_row - 1, Row_Destination - 1, -1):
            if ThisChessBoard.ChessBoardAll[k + 1, Location_col].IfUpBoard:
                flag_UpNowBoard = False
                break
        if flag_DownNowBoard and flag_UpNowBoard:
            flag_NoBoard = True
        else:
            flag_NoBoard = False

        if flag_NoBoard:
            self.Astar_Stop = True
            self.Min_DistanceLength = abs(Row_Destination - Location_row) + CloseList[len(CloseList) - 1].G
            # region 迭代寻找最短路径
            MinRoad = []
            if Player == 0:
                self.Player1MinRoad = []
                MinRoad = self.Player1MinRoad
            else:
                self.Player2MinRoad = []
                MinRoad = self.Player2MinRoad

            if Location_row < Row_Destination:
                for i in range(Row_Destination, Location_row - 1, -1):
                    MinRoad.append(Point(i, Location_col))
            else:
                for i in range(Row_Destination, Location_row + 1):
                    MinRoad.append(Point(i, Location_col))
            ALBuff = CloseList[len(CloseList) - 1]
            while True:
                if not isinstance(ALBuff.Father, type(1)):
                    MinRoad.append(Point(ALBuff.Father.Grid_row, ALBuff.Father.Grid_col))
                    ALBuff = ALBuff.Father
                else:
                    break
            # endregion
            return self.Min_DistanceLength
        # endregion

        # region 搜索树搜索策略——A*算法
        P_Dis = []
        for i in range(0, len(P_List_Enable)):
            P_Dis.append(999)
        minF = 9999
        minindex = 0

        i = 0
        while 0 <= i < len(P_List_Enable):
            Hbuff = abs(P_List_Enable[i].X - Row_Destination)
            P_Dis[i] = Hbuff
            Gbuff = num_renew
            Fbuff = Hbuff + Gbuff
            flag_InClose = False
            # 检测是否在Close列表里
            for j in range(0, len(CloseList)):
                if P_List_Enable[i].X == CloseList[j].Grid_row and P_List_Enable[i].Y == CloseList[j].Grid_col:
                    del P_List_Enable[i]
                    del P_Dis[i]
                    i -= 1
                    flag_InClose = True
                    break
            if flag_InClose:
                continue

            flag_InOpen = False
            # 检测是否在Open列表里
            for j in range(0, len(OpenList)):
                if P_List_Enable[i].X == OpenList[j].Grid_row and P_List_Enable[i].Y == OpenList[j].Grid_col:
                    del P_List_Enable[i]
                    del P_Dis[i]
                    i -= 1
                    flag_InOpen = True

                    if Gbuff < OpenList[j].G:
                        OpenList[j].G = Gbuff
                        OpenList[j].F = Fbuff
                        OpenList[j].H = Hbuff
                        OpenList[j].Father = NowGrid

                    break
            if (not flag_InOpen) and (not flag_InClose):
                NewGrid = self.AstarList(Hbuff, Gbuff, Fbuff, P_List_Enable[i].X, P_List_Enable[i].Y, NowGrid)
                OpenList.append(NewGrid)
            i += 1

        MinFGrid = self.AstarList(-1, -1, -1, -1, -1)
        for i in range(0, len(OpenList)):
            Fbuff = OpenList[i].F
            if Fbuff < minF:
                minF = Fbuff
                minindex = i
                MinFGrid = OpenList[i]

        CloseList.append(MinFGrid)

        dislengthbuff = 0
        if MinFGrid.Grid_row == Row_Destination and (not self.Astar_Stop):
            self.Min_DistanceLength += MinFGrid.G
            self.Astar_Stop = True
            return self.Min_DistanceLength
        else:
            if len(OpenList) > 0:
                OpenList.remove(MinFGrid)
                dislengthbuff = self.LookupRoad_Astar(ThisChessBoard, Player, MinFGrid, MinFGrid.G + 1, OpenList, CloseList)
            else:
                return 999
        # endregion
        return dislengthbuff


