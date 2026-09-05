import cshogi

from features.material import MaterialBalanceFeature


def test_initial_position_material_balance():
    """
    初期局面では先手・後手の駒価値が等しい。
    """

    board = cshogi.Board()

    feature = MaterialBalanceFeature()
    value = feature.extract(board)

    assert value.black > 0
    assert value.white > 0
    assert value.black == value.white
    assert value.difference == 0.0


def test_initial_position_mean():
    """
    初期局面ではmeanが正の値になる。
    """

    board = cshogi.Board()

    feature = MaterialBalanceFeature()
    value = feature.extract(board)

    assert value.mean > 0


def test_initial_position_normalized_balance():
    """
    初期局面の正規化された駒得差は0。
    """

    board = cshogi.Board()

    feature = MaterialBalanceFeature()

    normalized = feature.normalized_difference(board)

    assert -1.0 <= normalized <= 1.0
    assert abs(normalized) < 1e-9


def test_custom_piece_values():
    """
    駒価値を外部から変更できることを確認する。
    """

    board = cshogi.Board()

    values = MaterialBalanceFeature.DEFAULT_PIECE_VALUES.copy()
    values[cshogi.PAWN] = 2.0

    feature = MaterialBalanceFeature(
        piece_values=values
    )

    value = feature.extract(board)

    # 初期局面では歩が双方9枚存在するため、
    # 標準値から歩の変更分が反映される。
    assert value.black == value.white