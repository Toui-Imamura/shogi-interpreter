"""
exchange.py

F03: 駒交換による戦力変化

2つの局面を比較し、駒交換に伴う戦力・駒構成の変化を
抽出する特徴量。

F03はB分類の特徴量であり、単一局面の評価ではなく、
変化前局面と変化後局面の比較を基本とする。
"""

import math
from dataclasses import dataclass

import cshogi

from .base import Feature, FeatureValue


# ============================================================
# 駒価値
# ============================================================

PIECE_VALUES = {
    cshogi.PAWN: 1.0,
    cshogi.LANCE: 3.0,
    cshogi.KNIGHT: 3.0,
    cshogi.SILVER: 5.0,
    cshogi.BISHOP: 8.0,
    cshogi.ROOK: 9.0,
    cshogi.GOLD: 6.0,
    cshogi.KING: 0.0,
    cshogi.PROM_PAWN: 9.0,
    cshogi.PROM_LANCE: 9.0,
    cshogi.PROM_KNIGHT: 9.0,
    cshogi.PROM_SILVER: 9.0,
    cshogi.PROM_BISHOP: 11.0,
    cshogi.PROM_ROOK: 12.0,
}


# 大駒
MAJOR_PIECES = {
    cshogi.BISHOP,
    cshogi.ROOK,
    cshogi.PROM_BISHOP,
    cshogi.PROM_ROOK,
}


# 小駒
MINOR_PIECES = {
    cshogi.PAWN,
    cshogi.LANCE,
    cshogi.KNIGHT,
    cshogi.SILVER,
    cshogi.GOLD,
    cshogi.PROM_PAWN,
    cshogi.PROM_LANCE,
    cshogi.PROM_KNIGHT,
    cshogi.PROM_SILVER,
}


@dataclass(frozen=True)
class ExchangeMetrics:
    """
    2局面間の駒交換に関する内部指標。
    """

    exchange_count: float
    exchanged_value: float
    major_exchange_value: float
    minor_exchange_value: float
    board_to_hand_value: float
    composition_change: float


class ExchangeFeature(Feature):
    """
    F03 駒交換による戦力変化

    分類:
        B

    2局面間の変化から駒交換に関する情報を抽出する。
    """

    feature_id = "F03"
    name = "駒交換による戦力変化"
    category = "Material"
    classification = "B"

    NORMALIZATION_SCALE = 20.0

    def extract(self, board) -> FeatureValue:
        """
        Featureインターフェースとの互換性のための実装。

        F03は局面間の比較を前提とするため、
        単一局面では変化量を定義せず0を返す。
        """

        return FeatureValue(
            black=0.0,
            white=0.0,
        )

    def extract_transition(
        self,
        before_board,
        after_board,
    ) -> FeatureValue:
        """
        変化前局面と変化後局面を比較する。

        Parameters
        ----------
        before_board:
            変化前のcshogi.Board

        after_board:
            変化後のcshogi.Board

        Returns
        -------
        FeatureValue
            駒交換による変化量
        """

        metrics = self.calculate_metrics(
            before_board,
            after_board,
        )

        value = (
            metrics.exchanged_value
            + metrics.major_exchange_value
            + metrics.minor_exchange_value
            + metrics.board_to_hand_value
            + metrics.composition_change
        )

        normalized = self._normalize(value)

        return FeatureValue(
            black=normalized,
            white=normalized,
        )

    def calculate_metrics(
        self,
        before_board,
        after_board,
    ) -> ExchangeMetrics:
        """
        2局面間の駒交換に関する内部指標を計算する。
        """

        before_board_counts = self._count_board_pieces(
            before_board
        )

        after_board_counts = self._count_board_pieces(
            after_board
        )

        before_hand_counts = self._count_hand_pieces(
            before_board
        )

        after_hand_counts = self._count_hand_pieces(
            after_board
        )

        # ----------------------------------------------------
        # 盤上から減少した駒
        # ----------------------------------------------------

        exchanged_value = 0.0
        major_exchange_value = 0.0
        minor_exchange_value = 0.0
        exchange_count = 0.0

        for piece_type, value in PIECE_VALUES.items():

            if piece_type == cshogi.KING:
                continue

            before_count = before_board_counts.get(
                piece_type,
                0,
            )

            after_count = after_board_counts.get(
                piece_type,
                0,
            )

            decrease = max(
                0,
                before_count - after_count,
            )

            if decrease == 0:
                continue

            exchange_count += decrease

            exchanged = value * decrease
            exchanged_value += exchanged

            if piece_type in MAJOR_PIECES:
                major_exchange_value += exchanged

            elif piece_type in MINOR_PIECES:
                minor_exchange_value += exchanged

        # ----------------------------------------------------
        # 持ち駒への移行
        # ----------------------------------------------------

        before_hand_value = self._hand_value(
            before_hand_counts
        )

        after_hand_value = self._hand_value(
            after_hand_counts
        )

        board_to_hand_value = max(
            0.0,
            after_hand_value - before_hand_value,
        )

        # ----------------------------------------------------
        # 駒構成の変化
        # ----------------------------------------------------

        composition_change = (
            self._calculate_composition_change(
                before_board_counts,
                after_board_counts,
                before_hand_counts,
                after_hand_counts,
            )
        )

        return ExchangeMetrics(
            exchange_count=exchange_count,
            exchanged_value=exchanged_value,
            major_exchange_value=major_exchange_value,
            minor_exchange_value=minor_exchange_value,
            board_to_hand_value=board_to_hand_value,
            composition_change=composition_change,
        )

    def _count_board_pieces(self, board):
        """
        盤上に存在する駒を種類ごとに数える。
        """

        counts = {
            piece_type: 0
            for piece_type in PIECE_VALUES
        }

        for square in range(81):

            piece_type = board.piece_type(square)

            if piece_type in counts:
                counts[piece_type] += 1

        return counts

    def _count_hand_pieces(self, board):
        """
        持ち駒を種類ごとに数える。
        """

        counts = {
            cshogi.PAWN: 0,
            cshogi.LANCE: 0,
            cshogi.KNIGHT: 0,
            cshogi.SILVER: 0,
            cshogi.GOLD: 0,
            cshogi.BISHOP: 0,
            cshogi.ROOK: 0,
        }

        for hand in board.pieces_in_hand:

            for index, piece_type in enumerate(
                counts.keys()
            ):

                if index < len(hand):
                    counts[piece_type] += hand[index]

        return counts

    def _hand_value(self, hand_counts):
        """
        持ち駒の合計価値を計算する。
        """

        return sum(
            PIECE_VALUES[piece_type] * count
            for piece_type, count in hand_counts.items()
        )

    def _calculate_composition_change(
        self,
        before_board_counts,
        after_board_counts,
        before_hand_counts,
        after_hand_counts,
    ):
        """
        盤上＋持ち駒を含めた駒構成の変化を計算する。
        """

        change = 0.0

        for piece_type, value in PIECE_VALUES.items():

            if piece_type == cshogi.KING:
                continue

            before_total = (
                before_board_counts.get(
                    piece_type,
                    0,
                )
                + before_hand_counts.get(
                    piece_type,
                    0,
                )
            )

            after_total = (
                after_board_counts.get(
                    piece_type,
                    0,
                )
                + after_hand_counts.get(
                    piece_type,
                    0,
                )
            )

            difference = abs(
                after_total - before_total
            )

            change += value * difference

        return change

    def _normalize(self, value):
        """
        値を[-1, 1]の範囲へ正規化する。
        """

        return math.tanh(
            value / self.NORMALIZATION_SCALE
        )
