#!/usr/bin/env python 
# -*- coding:utf-8 -*-
import numpy as np
import tensorflow as tf


class PolicyValueNet:

    def policy_value(self, state_batch):
        """
        :param state_batch: 一堆棋局
        :return: 一堆动作P值和局面V值
        """
        pass

    def policy_value_fn(self, board):
        """
        论文里面的神经网络函数(p,v)=f(s)。
        :param board: 棋局
        :return: (action, probability)列表和v值
        """
        pass

    def train_step(self, state_batch, mcts_probs, winner_batch, lr):
        """
        训练一下。
        :param state_batch: 输入给神经网络的数据
        :param mcts_probs: 动作概率标签
        :param winner_batch: 胜率标签
        :param lr: 学习速度
        :return: 损失函数值和熵值
        """
        pass

    def save_model(self, model_path):
        """
        保存模型。
        :param model_path: 模型保存路径
        """
        pass

    def restore_model(self, model_path):
        """
        载入模型。
        :param model_path: 模型载入路径
        """
        pass


class GobangPolicyValueNet2(PolicyValueNet):
    def __init__(self, board_width, model_file=None):
        self.board_width = board_width

        # 定义网络结构
        # 1. 输入
        self.input_states = tf.placeholder(tf.float32, shape=[None, 4, board_width, board_width], name="input_states")
        self.input_state = tf.transpose(self.input_states, [0, 2, 3, 1], name="input_state")
        # 2. 中间层
        # 2.1 卷积层
        X = tf.layers.conv2d(inputs=self.input_state, filters=64, kernel_size=[3, 3], padding="same", data_format="channels_last")
        X = tf.layers.batch_normalization(X, axis=3)
        X = tf.nn.relu(X)

        # 2.2 残差层
        def residual_block(input):
            X = tf.layers.conv2d(inputs=input, filters=64, kernel_size=[3, 3], padding="same", data_format="channels_last")
            X = tf.layers.batch_normalization(X, axis=3)
            X = tf.nn.relu(X)

            X = tf.layers.conv2d(inputs=X, filters=64, kernel_size=[3, 3], padding="same", data_format="channels_last")
            X = tf.layers.batch_normalization(X, axis=3)

            add = tf.add(X, input)
            return tf.nn.relu(add)

        for i in range(4):
            X = residual_block(X)
        # 3. P数组输出
        Y = tf.layers.conv2d(inputs=X, filters=2, kernel_size=[1, 1], padding="same", data_format="channels_last")
        Y = tf.layers.batch_normalization(Y, axis=3)
        Y = tf.nn.relu(Y)
        self.action_conv_flat = tf.reshape(Y, [-1, 2 * board_width * board_width], name="action_conv_flat")
        self.action_fc = tf.layers.dense(inputs=self.action_conv_flat, units=board_width * board_width,
                                         activation=tf.nn.log_softmax, name="action_fc")
        # 4. v值输出
        Y = tf.layers.conv2d(inputs=X, filters=1, kernel_size=[1, 1], padding="same", data_format="channels_last")
        Y = tf.layers.batch_normalization(Y, axis=3)
        Y = tf.nn.relu(Y)
        self.evaluation_conv_flat = tf.reshape(Y, [-1, 1 * board_width * board_width], name="evaluation_conv_flat")
        self.evaluation_fc1 = tf.layers.dense(inputs=self.evaluation_conv_flat, units=64, activation=tf.nn.relu, name="evaluation_fc1")
        self.evaluation_fc2 = tf.layers.dense(inputs=self.evaluation_fc1, units=1, activation=tf.nn.tanh, name="evaluation_fc2")

        # 定义损失函数
        # 1. v值损失函数
        self.labels = tf.placeholder(tf.float32, shape=[None, 1], name="labels")  # 标记游戏的输赢，对应self.evaluation_fc2
        self.value_loss = tf.losses.mean_squared_error(self.labels, self.evaluation_fc2)
        # 2. P数组损失函数
        self.mcts_probs = tf.placeholder(tf.float32, shape=[None, board_width * board_width], name="mcts_probs")
        self.policy_loss = tf.negative(tf.reduce_mean(tf.reduce_sum(tf.multiply(self.mcts_probs, self.action_fc), 1)), name="policy_loss")
        # 3. L2正则项
        l2_penalty_beta = 1e-4
        vars = tf.trainable_variables()
        l2_penalty = l2_penalty_beta * tf.add_n([tf.nn.l2_loss(v) for v in vars if 'bias' not in v.name.lower()])
        # 4. 所有加起来成为损失函数
        self.loss = self.value_loss + self.policy_loss + l2_penalty

        # 计算熵值
        self.entropy = tf.negative(tf.reduce_mean(tf.reduce_sum(tf.exp(self.action_fc) * self.action_fc, 1)), name="entropy")

        # 训练用的优化器
        self.learning_rate = tf.placeholder(tf.float32, name="learning_rate")
        self.optimizer = tf.train.AdamOptimizer(learning_rate=self.learning_rate, name="optimizer").minimize(self.loss)

        # tensorflow的session
        self.session = tf.Session()
        self.session.run(tf.global_variables_initializer())

        # 模型的存储
        self.saver = tf.train.Saver(max_to_keep=123456789)  # max_to_keep设置一个很大的值防止保存的中间模型被删除
        if model_file is not None:
            self.restore_model(model_file)

    def policy_value(self, state_batch):
        state_batch = np.array(state_batch)
        log_act_probs, value = self.session.run(
                [self.action_fc, self.evaluation_fc2],
                feed_dict={self.input_states: state_batch})
        act_probs = np.exp(log_act_probs)
        return act_probs, value

    def policy_value_fn(self, board):
        legal_moves = board.get_available_moves()
        current_state = np.ascontiguousarray(board.current_state().reshape(
                -1, 4, self.board_width, self.board_width))
        act_probs, value = self.policy_value(current_state)
        act_probs = zip(legal_moves, act_probs[0][legal_moves])
        return act_probs, value

    def train_step(self, state_batch, mcts_probs, winner_batch, lr):
        winner_batch = np.reshape(winner_batch, (-1, 1))
        loss, entropy, _ = self.session.run(
                [self.loss, self.entropy, self.optimizer],
                feed_dict={self.input_states: state_batch,
                           self.mcts_probs: mcts_probs,
                           self.labels: winner_batch,
                           self.learning_rate: lr})
        return loss, entropy

    def save_model(self, model_path):
        self.saver.save(self.session, model_path)

    def restore_model(self, model_path):
        self.saver.restore(self.session, model_path)


class QuoridorPolicyValueNet(PolicyValueNet):
    def __init__(self, board_width, model_file=None):
        self.board_width = board_width

        # 定义网络结构
        # 1. 输入
        self.input_states = tf.placeholder(tf.float32, shape=[None, 4, board_width, board_width], name="input_states")
        self.input_state = tf.transpose(self.input_states, [0, 2, 3, 1], name="input_state")
        # 2. 中间层
        # 2.1 卷积层
        X = tf.layers.conv2d(inputs=self.input_state, filters=64, kernel_size=[3, 3], padding="same", data_format="channels_last")
        X = tf.layers.batch_normalization(X, axis=3)
        X = tf.nn.relu(X)

        # 2.2 残差层
        def residual_block(input):
            X = tf.layers.conv2d(inputs=input, filters=64, kernel_size=[3, 3], padding="same", data_format="channels_last")
            X = tf.layers.batch_normalization(X, axis=3)
            X = tf.nn.relu(X)

            X = tf.layers.conv2d(inputs=X, filters=64, kernel_size=[3, 3], padding="same", data_format="channels_last")
            X = tf.layers.batch_normalization(X, axis=3)

            add = tf.add(X, input)
            return tf.nn.relu(add)

        for i in range(4):
            X = residual_block(X)
        # 3. P数组输出
        Y = tf.layers.conv2d(inputs=X, filters=4, kernel_size=[1, 1], padding="same", data_format="channels_last")
        Y = tf.layers.batch_normalization(Y, axis=3)
        Y = tf.nn.relu(Y)
        self.action_conv_flat = tf.reshape(Y, [-1, 4, board_width * board_width], name="action_conv_flat")
        self.action_fc = tf.layers.dense(inputs=self.action_conv_flat, units=board_width * board_width,
                                         activation=tf.nn.log_softmax, name="action_fc")
        # 4. v值输出
        Y = tf.layers.conv2d(inputs=X, filters=1, kernel_size=[1, 1], padding="same", data_format="channels_last")
        Y = tf.layers.batch_normalization(Y, axis=3)
        Y = tf.nn.relu(Y)
        self.evaluation_conv_flat = tf.reshape(Y, [-1, 1 * board_width * board_width], name="evaluation_conv_flat")
        self.evaluation_fc1 = tf.layers.dense(inputs=self.evaluation_conv_flat, units=64, activation=tf.nn.relu, name="evaluation_fc1")
        self.evaluation_fc2 = tf.layers.dense(inputs=self.evaluation_fc1, units=1, activation=tf.nn.tanh, name="evaluation_fc2")

        # 定义损失函数
        # 1. v值损失函数
        self.labels = tf.placeholder(tf.float32, shape=[None, 1], name="labels")  # 标记游戏的输赢，对应self.evaluation_fc2
        self.value_loss = tf.losses.mean_squared_error(self.labels, self.evaluation_fc2)
        # 2. P数组损失函数
        self.mcts_probs = tf.placeholder(tf.float32, shape=[None, 4, board_width * board_width], name="mcts_probs")
        self.policy_loss = tf.negative(tf.reduce_mean(tf.reduce_sum(tf.multiply(self.mcts_probs, self.action_fc), 1)), name="policy_loss")
        # 3. L2正则项
        l2_penalty_beta = 1e-4
        vars = tf.trainable_variables()
        l2_penalty = l2_penalty_beta * tf.add_n([tf.nn.l2_loss(v) for v in vars if 'bias' not in v.name.lower()])
        # 4. 所有加起来成为损失函数
        self.loss = self.value_loss + self.policy_loss + l2_penalty

        # 计算熵值
        self.entropy = tf.negative(tf.reduce_mean(tf.reduce_sum(tf.exp(self.action_fc) * self.action_fc, 1)), name="entropy")

        # 训练用的优化器
        self.learning_rate = tf.placeholder(tf.float32, name="learning_rate")
        self.optimizer = tf.train.AdamOptimizer(learning_rate=self.learning_rate, name="optimizer").minimize(self.loss)

        # tensorflow的session
        self.session = tf.Session()
        self.session.run(tf.global_variables_initializer())

        # 模型的存储
        self.saver = tf.train.Saver(max_to_keep=123456789)  # max_to_keep设置一个很大的值防止保存的中间模型被删除
        if model_file is not None:
            self.restore_model(model_file)

    def policy_value(self, state_batch):
        state_batch = np.array(state_batch)
        log_act_probs, value = self.session.run(
                [self.action_fc, self.evaluation_fc2],
                feed_dict={self.input_states: state_batch})
        act_probs = np.exp(log_act_probs)
        return act_probs, value

    def policy_value_fn(self, board):
        legal_moves = board.get_available_moves()
        current_state = np.ascontiguousarray(board.current_state().reshape(
                -1, 4, self.board_width, self.board_width))
        act_probs, value = self.policy_value(current_state)
        act_probs = zip(legal_moves, act_probs[0][legal_moves])
        return act_probs, value

    def train_step(self, state_batch, mcts_probs, winner_batch, lr):
        winner_batch = np.reshape(winner_batch, (-1, 1))
        loss, entropy, _ = self.session.run(
                [self.loss, self.entropy, self.optimizer],
                feed_dict={self.input_states: state_batch,
                           self.mcts_probs: mcts_probs,
                           self.labels: winner_batch,
                           self.learning_rate: lr})
        return loss, entropy

    def save_model(self, model_path):
        self.saver.save(self.session, model_path)

    def restore_model(self, model_path):
        self.saver.restore(self.session, model_path)