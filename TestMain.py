#!/usr/bin/env python 
# -*- coding:utf-8 -*-
from Quoridor.VPNetModel import GobangPolicyValueNet2
from Quoridor.ModelTrain import Train
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # 屏蔽警告


def main():
    PVN2 = GobangPolicyValueNet2(10)
    T1 = Train(PVN2)

    T1.run()

    print("训练完成!")
    a = input()


main()
