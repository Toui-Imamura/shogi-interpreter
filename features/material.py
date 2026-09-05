import math

import cshogi

from .base import Feature, FeatureValue


class MaterialBalanceFeature(Feature):
    """
    F01: 駒得差

    現在局面の盤上に存在する駒の価値を
    先手・後手それぞれについて合計し、その差を求める。

    持ち駒はF02で扱うため、本特徴量には含めない。
    """

    feature_id = "F01"
    name = "駒得差"
    category = "Material"
    classification = "A"

    # ------------------------------------------------------------
    # 駒価値
    # ------------------------------------------------------------
    #
    # 現段階では初期パラメータ。
    # 将来的には棋譜データ等から調整・学習することを想定する。
    #
    # key:
    #     cshogiのpiece_type
    #
    # value:
    #     駒価値
    #
    # 成駒は元の駒とは別の価値として扱う。
    # ------------------------------------------------------------

    DEFAULT_PIECE_VALUES = {
        cshogi.PAWN: 1.0,
        cshogi.LANCE: 3.0,
        cshogi.KNIGHT: 3.0,
        cshogi.SILVER: 5.0,
        cshogi.BISHOP: 8.0,
        cshogi.ROOK: 9.0,
        cshogi.GOLD: 6.0,

        cshogi.PROM_PAWN: 9.0,
        cshogi.PROM_LANCE: 9.0,
        cshogi.PROM_KNIGHT: 9.0,
        cshogi.PROM_SILVER: 9.0,
        cshogi.PROM_BISHOP: 11.0,
        cshogi.PROM_ROOK: 12.0,

        # 玉は通常、駒得の計算対象から除外する。
        cshogi.KING: 0.0,
    }

    def __init__(
        self,
        piece_values: dict[int, float] | None = None,
        normalization_scale: float = 20.0,
    ):
        """
        Parameters
        ----------
        piece_values:
            駒種ごとの価値。
            Noneの場合はDEFAULT_PIECE_VALUESを使用する。

        normalization_scale:
            正規化時のスケール。
            現段階では実験用パラメータ。
        """

        if piece_values is None:
            self.piece_values = self.DEFAULT_PIECE_VALUES.copy()
        else:
            self.piece_values = piece_values.copy()

        if normalization_scale <= 0:
            raise ValueError(
                "normalization_scale must be greater than 0."
            )

        self.normalization_scale = normalization_scale

    def _piece_value(self, piece_type: int) -> float:
        """
        piece_typeから駒価値を取得する。
        """

        if piece_type not in self.piece_values:
            raise ValueError(
                f"Unknown piece type: {piece_type}"
            )

        return self.piece_values[piece_type]

    def extract(self, board) -> FeatureValue:
        """
        現在局面の盤上の駒得を計算する。

        Returns
        -------
        FeatureValue
            black:
                先手の盤上駒価値合計
            white:
                後手の盤上駒価値合計
        """

        black_value = 0.0
        white_value = 0.0

        for square in range(81):
            piece = board.piece(square)

            if piece == cshogi.NONE:
                continue

            # cshogiではsquareを渡してpiece_typeを取得する。
            piece_type = board.piece_type(square)

            value = self._piece_value(piece_type)

            # cshogiの駒コードから所属を判定する。
            #
            # piece < 16:
            #     先手
            #
            # piece >= 16:
            #     後手
            #
            # この判定は今回確認したcshogi 1.0.4の
            # 駒コード体系に基づく。
            if piece < 16:
                black_value += value
            else:
                white_value += value

        return FeatureValue(
            black=black_value,
            white=white_value,
        )

    def normalized_difference(self, board) -> float:
        """
        駒得差を[-1, 1]程度に正規化する。

        tanhを使用することで、大きな駒得差があっても
        値が過度に大きくならないようにする。
        """

        feature = self.extract(board)

        return math.tanh(
            feature.difference / self.normalization_scale
        )